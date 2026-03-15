"""Bootstrap the GAIA 8-core substrate with dual-plane storage.

.gaia_state/ layout
---------------------
.gaia_state/
  identity/        -- IdentityRoot (node_id, public key, genesis timestamp)
  memory/          -- CausalMemoryLog (append-only JSONL event stream)
  checkpoints/     -- CheckpointStore + OverlayRuntime snapshot index
  objects/         -- content-addressed raw object store (2-char sharding)
  semantic/        -- SemanticIndex (JSONL-backed rich metadata plane)
  views/           -- ViewManifest JSON files (one per registered view)
  system/          -- read-only system plane (OverlayRuntime, created on demand)
  data/            -- writable data plane   (OverlayRuntime, created on demand)

All directories are created by build_default_gaia() on first run.
Backward compatibility: legacy paths (identity/root.json, memory/events.jsonl,
checkpoints/) are preserved unchanged.

The returned GaiaSubstrate carries the dual-plane storage layer as first-class
fields: substrate.object_store and substrate.view_registry.
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
from gaia_core.storage.schemas import PlaneLayout


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

    The returned substrate carries:
      - legacy continuity plane: identity, memory, checkpoints, workspace
      - dual-plane storage: object_store (ObjectSubstrate), view_registry
        (NamespaceViewRegistry with standard GAIA views pre-registered)

    Parameters
    ----------
    root:
        Filesystem path for the GAIA state directory.  Defaults to
        ``.gaia_state`` in the current working directory.

    Returns
    -------
    GaiaSubstrate
        Ready-to-use substrate.  Access storage via::

            substrate.object_store   # ObjectSubstrate
            substrate.view_registry  # NamespaceViewRegistry
            substrate.has_storage    # True
    """
    root = Path(root)

    # ------------------------------------------------------------------
    # Ensure full .gaia_state/ layout exists
    # ------------------------------------------------------------------
    layout = PlaneLayout(root)
    layout.ensure_all()

    # ------------------------------------------------------------------
    # Legacy continuity plane (paths preserved for backward compat)
    # ------------------------------------------------------------------
    identity_path = layout.identity / "root.json"
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

    memory = CausalMemoryLog(layout.memory / "events.jsonl")
    checkpoints = CheckpointStore(layout.checkpoints)

    # ------------------------------------------------------------------
    # Dual-plane object + semantic storage
    # ------------------------------------------------------------------
    object_store = ObjectSubstrate(root)

    # Standard projection views wired to the semantic index
    view_registry = build_standard_views(
        index=object_store.index,
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

    # ------------------------------------------------------------------
    # Assemble and return the fully wired substrate
    # ------------------------------------------------------------------
    return GaiaSubstrate(
        registry=registry,
        identity=identity,
        memory=memory,
        checkpoints=checkpoints,
        workspace=workspace,
        object_store=object_store,
        view_registry=view_registry,
    )


# ---------------------------------------------------------------------------
# Module-level accessors for distro repos
# ---------------------------------------------------------------------------

def get_object_substrate(root: str | Path = ".gaia_state") -> ObjectSubstrate:
    """Return an ObjectSubstrate rooted at *root* (creates dirs if needed)."""
    return ObjectSubstrate(Path(root))
