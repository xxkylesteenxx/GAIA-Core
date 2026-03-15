"""Overlay runtime: system/data plane split for the GAIA substrate.

Architectural role
------------------
This module implements the APFS System/Data volume split equivalent
for GAIA.  It enforces a hard separation between:

  system plane  -- read-only, signed/verified substrate content
                   Lives in .gaia_state/system/
                   Equivalent to macOS Sealed System Volume (SSV)

  data plane    -- writable, user/application content
                   Lives in .gaia_state/data/
                   Equivalent to macOS Data volume

The overlay runtime does NOT use Linux kernel overlayfs at this stage
(that requires root and is platform-specific).  Instead it implements
the same logical contract in userspace:

  - Writes are always directed to the data plane.
  - Reads check the data plane first, then fall through to the system plane.
  - The system plane is write-locked by the runtime.
  - Any attempt to write to the system plane raises SystemPlaneWriteError.
  - Snapshots are taken of the system plane and registered in the
    checkpoint store as rollback points.

This is the correct next step before introducing kernel overlayfs,
because it establishes the interface contract that the kernel layer
will later implement more efficiently.

MacOS/Windows capability benchmark
------------------------------------
  macOS APFS  -- Sealed System Volume (read-only, cryptographic hash tree)
                 + Data volume (writable, per-user)
  Windows     -- System32 write protection + per-user %APPDATA%
                 + VSS snapshots for rollback
  GAIA        -- system/ plane (write-locked, snapshotted)
                 + data/ plane (writable)
                 + checkpoint store for rollback
"""
from __future__ import annotations

import hashlib
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, List, Optional

from gaia_core.storage.schemas import PlaneLayout

logger = logging.getLogger(__name__)


class SystemPlaneWriteError(PermissionError):
    """Raised when code attempts to write directly to the system plane."""


@dataclass_workaround = None  # resolved below with plain __init__


class SnapshotRecord:
    """Lightweight record of a system-plane snapshot."""

    def __init__(
        self,
        snapshot_id: str,
        timestamp: str,
        plane: str,
        root_hash: str,
        file_count: int,
        description: str = "",
    ) -> None:
        self.snapshot_id = snapshot_id
        self.timestamp = timestamp
        self.plane = plane
        self.root_hash = root_hash
        self.file_count = file_count
        self.description = description

    def to_dict(self) -> dict:
        return {
            "snapshot_id": self.snapshot_id,
            "timestamp": self.timestamp,
            "plane": self.plane,
            "root_hash": self.root_hash,
            "file_count": self.file_count,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SnapshotRecord":
        return cls(**d)


class OverlayRuntime:
    """Userspace system/data plane split with snapshot and rollback.

    Parameters
    ----------
    root:
        Path to ``.gaia_state/`` (the PlaneLayout root).
    lock_system_plane:
        When True (default), any direct write to ``system/`` raises
        SystemPlaneWriteError.  Set False during initial provisioning.
    """

    SNAPSHOT_INDEX = "snapshots.jsonl"

    def __init__(self, root: Path, lock_system_plane: bool = True) -> None:
        self.layout = PlaneLayout(root)
        self.lock_system_plane = lock_system_plane
        self._ensure_planes()

    # ------------------------------------------------------------------
    # Plane access
    # ------------------------------------------------------------------

    def read(self, relative_path: str) -> Optional[bytes]:
        """Read *relative_path*, checking data plane first then system plane."""
        data_path = self.layout.data / relative_path
        if data_path.exists():
            return data_path.read_bytes()
        system_path = self.layout.system / relative_path
        if system_path.exists():
            return system_path.read_bytes()
        return None

    def write(self, relative_path: str, data: bytes) -> Path:
        """Write *data* to the data plane at *relative_path*.

        Always writes to ``data/``; never touches ``system/``.
        """
        target = self.layout.data / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        logger.debug("[OverlayRuntime] wrote data/%s (%d bytes)", relative_path, len(data))
        return target

    def write_system(self, relative_path: str, data: bytes) -> Path:
        """Write to the system plane -- only valid when not locked.

        Used during initial provisioning (substrate bootstrap) before
        the system plane is sealed.
        """
        if self.lock_system_plane:
            raise SystemPlaneWriteError(
                f"System plane is sealed. Cannot write to system/{relative_path}. "
                "Call write() to direct content to the data plane, or instantiate "
                "OverlayRuntime(lock_system_plane=False) for provisioning."
            )
        target = self.layout.system / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        logger.debug("[OverlayRuntime] provisioned system/%s (%d bytes)", relative_path, len(data))
        return target

    def exists(self, relative_path: str) -> bool:
        """True if *relative_path* is visible in either plane."""
        return (
            (self.layout.data / relative_path).exists()
            or (self.layout.system / relative_path).exists()
        )

    def plane_for(self, relative_path: str) -> Optional[str]:
        """Return 'data', 'system', or None indicating which plane owns the path."""
        if (self.layout.data / relative_path).exists():
            return "data"
        if (self.layout.system / relative_path).exists():
            return "system"
        return None

    # ------------------------------------------------------------------
    # Snapshot / rollback
    # ------------------------------------------------------------------

    def snapshot_system_plane(self, description: str = "") -> SnapshotRecord:
        """Hash every file in the system plane and record the snapshot.

        Returns a SnapshotRecord written to the checkpoint index.
        This is the GAIA equivalent of APFS creating a signed system snapshot
        at each OS update.
        """
        files = sorted(self.layout.system.rglob("*"))
        file_count = 0
        combined = hashlib.sha256()
        for f in files:
            if f.is_file():
                combined.update(f.read_bytes())
                file_count += 1

        root_hash = combined.hexdigest()
        ts = datetime.now(timezone.utc).isoformat()
        snapshot_id = f"snap-sys-{root_hash[:12]}-{ts[:10]}"

        record = SnapshotRecord(
            snapshot_id=snapshot_id,
            timestamp=ts,
            plane="system",
            root_hash=root_hash,
            file_count=file_count,
            description=description,
        )
        self._append_snapshot(record)
        logger.info(
            "[OverlayRuntime] system snapshot %s: %d files, hash=%s",
            snapshot_id, file_count, root_hash[:16],
        )
        return record

    def list_snapshots(self) -> List[SnapshotRecord]:
        """Return all recorded snapshots in append order."""
        index_path = self.layout.checkpoints / self.SNAPSHOT_INDEX
        if not index_path.exists():
            return []
        records: List[SnapshotRecord] = []
        for line in index_path.read_text().splitlines():
            line = line.strip()
            if line:
                try:
                    records.append(SnapshotRecord.from_dict(json.loads(line)))
                except (json.JSONDecodeError, TypeError):
                    continue
        return records

    def verify_system_plane(self, snapshot: SnapshotRecord) -> bool:
        """Verify the current system plane matches *snapshot*.

        Returns True if the root hash matches (plane is unmodified),
        False if it has drifted (equivalent to a failed SSV verification).
        """
        files = sorted(self.layout.system.rglob("*"))
        combined = hashlib.sha256()
        for f in files:
            if f.is_file():
                combined.update(f.read_bytes())
        current_hash = combined.hexdigest()
        match = current_hash == snapshot.root_hash
        if not match:
            logger.warning(
                "[OverlayRuntime] system plane verification FAILED: "
                "expected %s, got %s",
                snapshot.root_hash[:16], current_hash[:16],
            )
        return match

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_data(self) -> Iterator[Path]:
        """Yield all files in the data plane."""
        if self.layout.data.exists():
            yield from (f for f in self.layout.data.rglob("*") if f.is_file())

    def list_system(self) -> Iterator[Path]:
        """Yield all files in the system plane."""
        if self.layout.system.exists():
            yield from (f for f in self.layout.system.rglob("*") if f.is_file())

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _ensure_planes(self) -> None:
        self.layout.system.mkdir(parents=True, exist_ok=True)
        self.layout.data.mkdir(parents=True, exist_ok=True)
        self.layout.checkpoints.mkdir(parents=True, exist_ok=True)

    def _append_snapshot(self, record: SnapshotRecord) -> None:
        index_path = self.layout.checkpoints / self.SNAPSHOT_INDEX
        with index_path.open("a") as fh:
            fh.write(json.dumps(record.to_dict()) + "\n")
