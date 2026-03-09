from __future__ import annotations

from pathlib import Path

from gaia_core.continuity.causal_memory import CausalMemoryLog
from gaia_core.continuity.checkpoints import CheckpointStore
from gaia_core.continuity.identity import IdentityRoot
from gaia_core.core.implementations import build_core_set
from gaia_core.core.registry import CoreRegistry
from gaia_core.core.substrate import GaiaSubstrate
from gaia_core.federation.workspace import CollectiveWorkspace


def build_default_gaia(root: str | Path = ".gaia_state") -> GaiaSubstrate:
    root = Path(root)
    identity_dir = root / "identity"
    memory_dir = root / "memory"
    checkpoint_dir = root / "checkpoints"
    identity_dir.mkdir(parents=True, exist_ok=True)
    identity_path = identity_dir / "root.json"

    identity = IdentityRoot.load(identity_path) if identity_path.exists() else IdentityRoot.create()
    if not identity_path.exists():
        identity.persist(identity_path)

    registry = CoreRegistry()
    for core in build_core_set():
        registry.register(core)

    memory = CausalMemoryLog(memory_dir / "events.jsonl")
    checkpoints = CheckpointStore(checkpoint_dir)
    workspace = CollectiveWorkspace(
        workspace_id="gaia-main",
        problem_frame="Bootstrap the GAIA 8-core substrate with continuity, grounding, and auditability.",
        goals=[
            "stabilize 8-core registry",
            "preserve continuity and checkpointing",
            "measure theory-linked evidence rather than marketing claims",
            "preserve dissent in federated coordination",
        ],
    )
    workspace.add_commitment("Bootstrap substrate initialized.")
    return GaiaSubstrate(
        registry=registry,
        identity=identity,
        memory=memory,
        checkpoints=checkpoints,
        workspace=workspace,
    )
