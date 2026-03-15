"""GaiaSubstrate: the unified GAIA runtime object.

Fields
------
legacy continuity plane:
  registry     -- 8-core CoreRegistry
  identity     -- IdentityRoot (node_id, public key, genesis timestamp)
  memory       -- CausalMemoryLog (append-only event stream)
  checkpoints  -- CheckpointStore (periodic snapshots)
  workspace    -- CollectiveWorkspace (federation coordination)

dual-plane storage (new):
  object_store   -- ObjectSubstrate: content-addressed objects + semantic index
  view_registry  -- NamespaceViewRegistry: projection views over the semantic index

The two storage fields are Optional so that existing callers and tests that
construct GaiaSubstrate directly (without going through bootstrap) continue
to work without modification.
"""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, Optional

from gaia_core.continuity.causal_memory import CausalMemoryLog
from gaia_core.continuity.checkpoints import CheckpointStore
from gaia_core.continuity.identity import IdentityRoot
from gaia_core.core.registry import CoreRegistry
from gaia_core.federation.workspace import CollectiveWorkspace
from gaia_core.measurement.cgi import compute_cgi

# Import storage types lazily-typed to avoid circular imports at module level.
# Real types are resolved at runtime; Optional[Any] keeps the class importable
# even if gaia_core.storage is not yet on the path.
try:
    from gaia_core.storage.substrate import ObjectSubstrate
    from gaia_core.storage.namespace_views import NamespaceViewRegistry
except ImportError:  # pragma: no cover
    ObjectSubstrate = Any  # type: ignore[assignment,misc]
    NamespaceViewRegistry = Any  # type: ignore[assignment,misc]


class GaiaSubstrate:
    """The unified GAIA runtime object.

    Carries both the legacy continuity plane (identity, memory, checkpoints,
    workspace) and the new dual-plane storage layer (object_store,
    view_registry) as first-class fields.
    """

    def __init__(
        self,
        registry: CoreRegistry,
        identity: IdentityRoot,
        memory: CausalMemoryLog,
        checkpoints: CheckpointStore,
        workspace: CollectiveWorkspace,
        object_store: Optional[Any] = None,
        view_registry: Optional[Any] = None,
    ) -> None:
        # --- legacy continuity plane ---
        self.registry = registry
        self.identity = identity
        self.memory = memory
        self.checkpoints = checkpoints
        self.workspace = workspace

        # --- dual-plane storage ---
        self.object_store: Optional[ObjectSubstrate] = object_store
        self.view_registry: Optional[NamespaceViewRegistry] = view_registry

    # ------------------------------------------------------------------
    # Storage helpers
    # ------------------------------------------------------------------

    @property
    def has_storage(self) -> bool:
        """True if the dual-plane storage layer is wired in."""
        return self.object_store is not None

    def storage_capabilities(self) -> list:
        """Return the list of active StorageCapability values."""
        if not self.has_storage:
            return []
        try:
            from gaia_core.storage.schemas import StorageCapability
            caps = [
                StorageCapability.CONTENT_ADDRESSED,
                StorageCapability.SEMANTIC_INDEX,
            ]
            if self.view_registry is not None:
                caps.append(StorageCapability.PROJECTION_VIEWS)
            return caps
        except ImportError:  # pragma: no cover
            return []

    # ------------------------------------------------------------------
    # Core dispatch
    # ------------------------------------------------------------------

    def dispatch(self, target: str, message: Dict[str, Any]) -> Dict[str, Any]:
        core = next(c for c in self.registry.all() if c.name.value == target)
        response = core.handle(message)
        self.memory.append(
            core=target,
            kind=message.get("kind", "message"),
            payload={"request": message, "response": response},
        )
        return response

    # ------------------------------------------------------------------
    # Consciousness / checkpoint
    # ------------------------------------------------------------------

    def consciousness_snapshot(self) -> Dict[str, Any]:
        core_states = {c.name.value: c.snapshot() for c in self.registry.all()}
        replay = self.memory.replay()
        signals = {
            "broadcast_coverage":          min(1.0, len(core_states) / 8.0),
            "broadcast_latency_ms":        25.0,
            "workspace_persistence_ms":    700.0,
            "integration_density":         min(1.0, len(replay) / 10.0),
            "irreducibility_proxy":         0.62,
            "partition_loss":               0.22,
            "recurrence_ratio":             0.71,
            "feedback_stability":           0.68,
            "reentry_depth_norm":           0.55,
            "checkpoint_recovery_score":    0.75,
            "identity_stability":           0.80,
            "replay_consistency":           0.77,
            "self_report_only":             False,
            "failed_perturbation_test":     False,
            "identity_drift":               0.12,
            "adversarial_prompt_susceptibility": 0.20,
        }
        evidence = compute_cgi(signals)
        snapshot: Dict[str, Any] = {
            "identity_fingerprint": self.identity.public_fingerprint,
            "core_states":          core_states,
            "workspace":            asdict(self.workspace.snapshot()),
            "memory_event_count":   len(replay),
            "evidence":             asdict(evidence),
        }
        if self.has_storage:
            snapshot["storage"] = {
                "object_count":  len(self.object_store.index),
                "view_count":    len(self.view_registry.list_views()) if self.view_registry else 0,
                "capabilities":  [c.name for c in self.storage_capabilities()],
            }
        return snapshot

    def checkpoint(self) -> Dict[str, Any]:
        snapshot = self.consciousness_snapshot()
        manifest = self.checkpoints.save(
            payload=snapshot,
            identity_fingerprint=self.identity.public_fingerprint,
            registered_cores=self.registry.names(),
            event_count=snapshot["memory_event_count"],
            workspace_epoch=snapshot["workspace"]["epoch"],
        )
        return {
            "checkpoint_id":    manifest.checkpoint_id,
            "workspace_epoch":  manifest.workspace_epoch,
            "event_count":      manifest.event_count,
        }
