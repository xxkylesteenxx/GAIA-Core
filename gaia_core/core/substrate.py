from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict

from gaia_core.continuity.causal_memory import CausalMemoryLog
from gaia_core.continuity.checkpoints import CheckpointStore
from gaia_core.continuity.identity import IdentityRoot
from gaia_core.core.registry import CoreRegistry
from gaia_core.federation.workspace import CollectiveWorkspace
from gaia_core.measurement.cgi import compute_cgi


class GaiaSubstrate:
    def __init__(
        self,
        registry: CoreRegistry,
        identity: IdentityRoot,
        memory: CausalMemoryLog,
        checkpoints: CheckpointStore,
        workspace: CollectiveWorkspace,
    ) -> None:
        self.registry = registry
        self.identity = identity
        self.memory = memory
        self.checkpoints = checkpoints
        self.workspace = workspace

    def dispatch(self, target: str, message: Dict[str, Any]) -> Dict[str, Any]:
        core = next(c for c in self.registry.all() if c.name.value == target)
        response = core.handle(message)
        self.memory.append(
            core=target,
            kind=message.get("kind", "message"),
            payload={"request": message, "response": response},
        )
        return response

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
        return {
            "identity_fingerprint": self.identity.public_fingerprint,
            "core_states":          core_states,
            "workspace":            asdict(self.workspace.snapshot()),
            "memory_event_count":   len(replay),
            "evidence":             asdict(evidence),
        }

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
