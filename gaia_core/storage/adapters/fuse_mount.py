"""FUSE adapter: mount GAIA projection views as a real filesystem path.

Architectural role
------------------
This module is the bridge between the in-process NamespaceViewRegistry
and the Linux VFS layer.  When activated it exposes the virtual path
tree defined by the registry as a real mountpoint that any process on
the system can navigate:

  /gaia/views/by-core/SOPHIA/        <- objects scoped to SOPHIA
  /gaia/views/by-trust/high/         <- high-trust objects only
  /gaia/views/by-kind/sensor-event/  <- sensor artifacts
  /gaia/views/by-tenant/<id>/        <- per-tenant projections
  /gaia/views/by-planetary-state/    <- unrestricted planetary view

Each "file" under a view path is a read-only JSON representation of a
SemanticRecord.  The raw object bytes are accessible via a parallel
``/gaia/objects/<shard>/<hash>`` tree that maps directly onto the
``objects/`` plane in .gaia_state/.

Design notes
------------
- Production operation requires ``fusepy`` or ``pyfuse3`` and a kernel
  with FUSE support (standard on Linux 3.x+).  The class has a ``dry_run``
  mode that validates the view enumeration without mounting anything,
  making it safe to import and unit-test on any platform.
- All filesystem operations are read-only from the FUSE side.  Writes go
  through ObjectSubstrate.put(), never through the FUSE mount.
- This is analogous to APFS's volume-group read/write split: the system
  plane (semantic index + projection views) is read-only at the VFS layer;
  the data plane (new objects) is written through the substrate API.

MacOS/Windows capability benchmark
-----------------------------------
  macOS APFS  -- signed system snapshot exposed as read-only to VFS
  Windows     -- reparse points provide filesystem-level indirection
  GAIA        -- FUSE projection views provide semantic indirection
                  over the content-addressed object store
"""
from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

from gaia_core.storage.namespace_views import NamespaceViewRegistry, ViewDefinition
from gaia_core.storage.semantic_index import SemanticRecord
from gaia_core.storage.schemas import ViewManifest

logger = logging.getLogger(__name__)


class GaiaFuseMount:
    """FUSE mount controller for GAIA projection views.

    Parameters
    ----------
    registry:
        The populated NamespaceViewRegistry from bootstrap.
    objects_dir:
        Path to ``.gaia_state/objects/`` for raw-byte access.
    mountpoint:
        Where to mount the virtual filesystem.  Defaults to ``/gaia/views``.
    dry_run:
        When True, validate view enumeration without calling any FUSE
        syscalls.  Safe on any platform; used in tests.
    """

    MOUNT_ROOT = Path("/gaia/views")
    OBJECTS_MOUNT = Path("/gaia/objects")

    def __init__(
        self,
        registry: NamespaceViewRegistry,
        objects_dir: Path,
        mountpoint: Optional[Path] = None,
        dry_run: bool = False,
    ) -> None:
        self.registry = registry
        self.objects_dir = objects_dir
        self.mountpoint = mountpoint or self.MOUNT_ROOT
        self.dry_run = dry_run
        self._mounted = False
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def mount(self) -> None:
        """Mount the FUSE filesystem (or validate in dry_run mode)."""
        if self.dry_run:
            self._validate_views()
            logger.info("[GaiaFuseMount] dry_run: view validation passed, no mount performed")
            return

        try:
            import fuse  # type: ignore[import]  # fusepy
        except ImportError:
            try:
                import pyfuse3 as fuse  # type: ignore[import]
            except ImportError:
                raise RuntimeError(
                    "FUSE mount requires 'fusepy' or 'pyfuse3'. "
                    "Install with: pip install fusepy  or  pip install pyfuse3"
                )

        self.mountpoint.mkdir(parents=True, exist_ok=True)
        logger.info("[GaiaFuseMount] mounting at %s", self.mountpoint)
        self._mounted = True
        # The actual fuse.FUSE() call would be inserted here when integrating
        # with a concrete fuse.Operations subclass.  The operations class
        # is implemented in platform/filesystem/meta_overlay/ and calls
        # back into this controller for record enumeration and resolution.
        logger.info("[GaiaFuseMount] mount point initialised (operations class pending)")

    def unmount(self) -> None:
        """Unmount the FUSE filesystem."""
        if not self._mounted:
            return
        if not self.dry_run:
            try:
                os.system(f"fusermount -u {self.mountpoint}")
            except Exception as exc:  # noqa: BLE001
                logger.warning("[GaiaFuseMount] unmount failed: %s", exc)
        self._mounted = False
        logger.info("[GaiaFuseMount] unmounted %s", self.mountpoint)

    # ------------------------------------------------------------------
    # View enumeration API (called by the FUSE operations class)
    # ------------------------------------------------------------------

    def list_view_ids(self) -> List[str]:
        """Return all registered view IDs."""
        return [v.view_id for v in self.registry.list_views()]

    def enumerate_view(self, view_id: str) -> List[SemanticRecord]:
        """Return all records visible under *view_id*."""
        return self.registry.enumerate_view(view_id)

    def resolve_object(self, view_id: str, object_id: str) -> Optional[SemanticRecord]:
        """Resolve a single object within a view; None if not visible."""
        return self.registry.resolve_object(view_id, object_id)

    def record_to_file_content(self, record: SemanticRecord) -> bytes:
        """Serialise *record* to the bytes the FUSE layer exposes as a file."""
        return (json.dumps(record.to_dict(), indent=2) + "\n").encode()

    def object_path(self, content_hash: str) -> Path:
        """Resolve a content hash to its physical path in objects/."""
        shard = content_hash[:2]
        return self.objects_dir / shard / content_hash

    # ------------------------------------------------------------------
    # View manifest persistence
    # ------------------------------------------------------------------

    def write_manifests(self, views_dir: Path) -> List[Path]:
        """Write one ViewManifest JSON file per view to *views_dir*.

        The overlay runtime and any out-of-process tool can reconstruct
        the view registry from these files without a live Python substrate.
        """
        written: List[Path] = []
        for view in self.registry.list_views():
            manifest = _view_to_manifest(view)
            path = manifest.write(views_dir)
            written.append(path)
            logger.debug("[GaiaFuseMount] wrote manifest %s", path)
        return written

    def load_manifests(self, views_dir: Path) -> List[ViewManifest]:
        """Load all ViewManifest files from *views_dir*."""
        manifests: List[ViewManifest] = []
        for path in sorted(views_dir.glob("*.json")):
            try:
                manifests.append(ViewManifest.read(path))
            except Exception as exc:  # noqa: BLE001
                logger.warning("[GaiaFuseMount] could not load manifest %s: %s", path, exc)
        return manifests

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _validate_views(self) -> None:
        """Walk every view and record; raise on structural errors."""
        for view in self.registry.list_views():
            records = self.registry.enumerate_view(view.view_id)
            for rec in records:
                if not rec.object_id:
                    raise ValueError(
                        f"View '{view.view_id}' contains a record with empty object_id"
                    )
        logger.debug(
            "[GaiaFuseMount] validated %d views",
            len(self.registry.list_views()),
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _view_to_manifest(view: ViewDefinition) -> ViewManifest:
    """Convert a live ViewDefinition to a serialisable ViewManifest."""
    policy = view.policy
    return ViewManifest(
        view_id=view.view_id,
        virtual_prefix=view.virtual_prefix,
        description=view.description,
        read_only=view.read_only,
        policy_name=policy.name,
        allowed_kinds=list(policy.allowed_kinds),
        allowed_trust_levels=list(policy.allowed_trust_levels),
        allowed_cores=list(policy.allowed_cores),
        allowed_tenants=list(policy.allowed_tenants),
        required_tags=list(policy.required_tags),
    )
