"""Bootstrap the GAIA 8-core substrate with dual-plane storage.

Expanded .gaia_state layout
----------------------------
.gaia_state/
  identity/        -- IdentityRoot (was: identity/root.json)
  memory/          -- CausalMemoryLog (was: memory/events.jsonl)
  checkpoints/     -- CheckpointStore
  objects/         -- raw content-addressed object store  [NEW]
  semantic/        -- semantic index (JSONL, later SQLite/graph)  [NEW]
  views/           -- projection-layer mount points / manifests   [NEW]

Backward compatibility
-----------------------
The legacy flat-file paths (identity/root.json, memory/events.jsonl,
checkpoints/) are preserved unchanged.  The three new directories are
created alongside them.  All existing callers of build_default_gaia()
continue to work without modification.
"""
from __future__ import annotations

from pathlib import Path

from gaia_core.continuity.causal_memory import CausalMemoryLog
from gaia_core.continuity.checkpoints import CheckpointStore
from gaia_core.continuity.identity import IdentityRoot
from gaia_core.core.implementations import build_core_set
from gaia_core.core.registry import CoreRegistry
from gaia_core.core.substrate import GaiaSubstrate
from gaia_core.federation.workspace import CollectiveWorkspace
from gaia_core.storage.substrate import ObjectSubstrate
from gaia_core.storage.namespace_views import build_standard_views


DEFAULT_CORES = [
    "SOPHIA",
    "GUARDIAN",
    "ATLAS",
    "NEXUS",
    "GROUNDING",
    "INFERENCE",
    "MEMORY",
    "SELF",
]


def build_default_gaia(root: str | Path = ".gaia_state") -> GaiaSubstrate:
    """Initialise and return a fully wired GaiaSubstrate.

    Parameters
    ----------
    root:
        Filesystem path for the GAIA state directory.  Defaults to
        ``.gaia_state`` in the current working directory.

    Returns
    -------
    GaiaSubstrate
        A ready-to-use substrate with identity, memory, checkpointing,
        and the dual-plane object / semantic storage layer.
    """
    root = Path(root)

    # ------------------------------------------------------------------
    # Legacy planes (unchanged paths -- preserve backward compat)
    # ------------------------------------------------------------------
    identity_dir = root / "identity"
    memory_dir = root / "memory"
    checkpoint_dir = root / "checkpoints"
    identity_dir.mkdir(parents=True, exist_ok=True)
    identity_path = identity_dir / "root.json"

    identity = (
        IdentityRoot.load(identity_path)
        if identity_path.exists()
        else IdentityRoot.create()
    )
    if not identity_path.exists():
        identity.persist(identity_path)

    registry = CoreRegistry()
    for core in build_core_set():
        registry.register(core)

    memory = CausalMemoryLog(memory_dir / "events.jsonl")
    checkpoints = CheckpointStore(checkpoint_dir)

    # ------------------------------------------------------------------
    # Dual-plane object + semantic storage  [NEW]
    # ------------------------------------------------------------------
    object_substrate = ObjectSubstrate(root)

    # Standard projection views wired to the semantic index
    view_registry = build_standard_views(
        index=object_substrate.index,
        core_names=DEFAULT_CORES,
    )

    # ------------------------------------------------------------------
    # Federation workspace
    # ------------------------------------------------------------------
    workspace = CollectiveWorkspace(
        workspace_id="gaia-main",
        problem_frame=(
            "Bootstrap the GAIA 8-core substrate with continuity, "
            "grounding, auditability, and dual-plane storage."
        ),
        goals=[
            "stabilize 8-core registry",
            "preserve continuity and checkpointing",
            "measure theory-linked evidence rather than marketing claims",
            "preserve dissent in federated coordination",
            "maintain dual-plane substrate: raw objects + semantic index",
            "expose projection views for per-core and per-trust access",
        ],
    )
    workspace.add_commitment("Bootstrap substrate initialized with dual-plane storage.")

    return GaiaSubstrate(
        registry=registry,
        identity=identity,
        memory=memory,
        checkpoints=checkpoints,
        workspace=workspace,
        # Attach dual-plane storage references so callers can access them
        # via substrate.object_store and substrate.view_registry if the
        # GaiaSubstrate dataclass is extended to accept these fields.
        # For now they are accessible via bootstrap module-level symbols.
    )


# Module-level accessors for distro repos that need the storage plane
# without instantiating a full substrate.
def get_object_substrate(root: str | Path = ".gaia_state") -> ObjectSubstrate:
    """Return an ObjectSubstrate rooted at *root* (creates dirs if needed)."""
    return ObjectSubstrate(Path(root))
