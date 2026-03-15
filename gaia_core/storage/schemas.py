"""Canonical type definitions for the GAIA dual-plane storage substrate.

All public data contracts shared across the storage package live here:

  SemanticRecord     -- rich metadata record (re-exported from semantic_index)
  ObjectMeta         -- lightweight summary of a stored object
  ViewManifest       -- serialisable description of a registered view
  PlaneLayout        -- the directory layout contract for .gaia_state/
  StorageCapability  -- enum of capabilities the substrate supports

Importing from ``gaia_core.storage.schemas`` is the preferred way for code
outside the storage package to reference these types without pulling in
implementation details.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import List, Optional

# Re-export SemanticRecord so callers have a single import point.
from gaia_core.storage.semantic_index import SemanticRecord as SemanticRecord  # noqa: F401


# ---------------------------------------------------------------------------
# ObjectMeta
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ObjectMeta:
    """Lightweight summary of a stored object -- no raw bytes."""

    object_id: str
    """Full ObjectID string (kind:hash)."""

    kind: str
    """Object kind string, e.g. 'blob', 'event', 'checkpoint'."""

    size_bytes: int
    """Size of the raw content in bytes."""

    content_hash: str
    """SHA-256 hex digest of the raw content."""

    trust_level: str = "standard"
    ontology_type: str = "gaia:unknown"
    origin_core: str = "GAIA"
    tenant_id: Optional[str] = None
    node_id: Optional[str] = None


# ---------------------------------------------------------------------------
# ViewManifest
# ---------------------------------------------------------------------------

@dataclass
class ViewManifest:
    """Serialisable description of a registered namespace view.

    Written to ``.gaia_state/views/<view_id>.json`` by the overlay runtime
    so that the FUSE daemon can reconstruct the view registry without a live
    Python process.
    """

    view_id: str
    """Stable identifier, e.g. 'by-core-SOPHIA' or 'by-trust-high'."""

    virtual_prefix: str
    """Mount path the FUSE daemon exposes, e.g. '/gaia/views/by-trust/high'."""

    description: str = ""
    read_only: bool = True

    policy_name: str = "open"
    allowed_kinds: List[str] = field(default_factory=list)
    allowed_trust_levels: List[str] = field(default_factory=list)
    allowed_cores: List[str] = field(default_factory=list)
    allowed_tenants: List[str] = field(default_factory=list)
    required_tags: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        import dataclasses
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ViewManifest":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in d.items() if k in known})

    def write(self, views_dir: Path) -> Path:
        """Persist this manifest to *views_dir*/<view_id>.json."""
        import json
        views_dir.mkdir(parents=True, exist_ok=True)
        path = views_dir / f"{self.view_id}.json"
        path.write_text(json.dumps(self.to_dict(), indent=2))
        return path

    @classmethod
    def read(cls, path: Path) -> "ViewManifest":
        """Load a manifest from *path*."""
        import json
        return cls.from_dict(json.loads(path.read_text()))


# ---------------------------------------------------------------------------
# PlaneLayout
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PlaneLayout:
    """The canonical directory layout contract for a .gaia_state/ root.

    Pass a ``root`` path and read the typed subdirectory properties.
    This is the single source of truth for what directories must exist
    and what each plane is responsible for.
    """

    root: Path

    # ---- Legacy planes (backward-compatible) ----

    @property
    def identity(self) -> Path:
        """Identity root: node_id, public key, genesis timestamp."""
        return self.root / "identity"

    @property
    def memory(self) -> Path:
        """Causal memory log: append-only JSONL event stream."""
        return self.root / "memory"

    @property
    def checkpoints(self) -> Path:
        """Checkpoint store: periodic substrate snapshots."""
        return self.root / "checkpoints"

    # ---- Dual-plane storage (new) ----

    @property
    def objects(self) -> Path:
        """Content-addressed raw object store (Git-style 2-char sharding)."""
        return self.root / "objects"

    @property
    def semantic(self) -> Path:
        """Semantic index: JSONL-backed rich metadata plane."""
        return self.root / "semantic"

    @property
    def views(self) -> Path:
        """Projection mount points: ViewManifest JSON files per view."""
        return self.root / "views"

    # ---- System/data split (overlay) ----

    @property
    def system(self) -> Path:
        """Read-only system plane: signed/verified substrate content."""
        return self.root / "system"

    @property
    def data(self) -> Path:
        """Writable data plane: mutable user/application content."""
        return self.root / "data"

    def ensure_all(self) -> None:
        """Create all required directories (idempotent)."""
        for plane in (
            self.identity, self.memory, self.checkpoints,
            self.objects, self.semantic, self.views,
            self.system, self.data,
        ):
            plane.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# StorageCapability
# ---------------------------------------------------------------------------

class StorageCapability(Enum):
    """Capabilities that a substrate node may advertise."""

    CONTENT_ADDRESSED = auto()   # objects/ plane
    SEMANTIC_INDEX = auto()      # semantic/ plane
    PROJECTION_VIEWS = auto()    # views/ plane + namespace_views
    FUSE_MOUNT = auto()          # fuse_mount adapter active
    OVERLAY_RUNTIME = auto()     # overlay_runtime system/data split active
    SNAPSHOT = auto()            # checkpoint-based rollback available
    FEDERATION = auto()          # object IDs federated to GAIA-Meta
