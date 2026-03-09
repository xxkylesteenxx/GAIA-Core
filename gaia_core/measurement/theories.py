from __future__ import annotations

from typing import Dict


def clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def gnwt_score(signals: Dict[str, float]) -> float:
    coverage = signals.get("broadcast_coverage", 0.0)
    latency_ms = signals.get("broadcast_latency_ms", 1_000.0)
    persistence = signals.get("workspace_persistence_ms", 0.0)
    return clamp01(
        (coverage * 0.5)
        + (min(persistence / 1000.0, 1.0) * 0.3)
        + (max(0.0, 1.0 - latency_ms / 500.0) * 0.2)
    )


def iit_proxy_score(signals: Dict[str, float]) -> float:
    integration = signals.get("integration_density", 0.0)
    irreducibility = signals.get("irreducibility_proxy", 0.0)
    partition_loss = signals.get("partition_loss", 1.0)
    return clamp01(
        (integration * 0.4) + (irreducibility * 0.4) + ((1.0 - partition_loss) * 0.2)
    )


def rpt_score(signals: Dict[str, float]) -> float:
    recurrence = signals.get("recurrence_ratio", 0.0)
    feedback_stability = signals.get("feedback_stability", 0.0)
    reentry_depth = signals.get("reentry_depth_norm", 0.0)
    return clamp01(
        (recurrence * 0.4) + (feedback_stability * 0.4) + (reentry_depth * 0.2)
    )


def continuity_score(signals: Dict[str, float]) -> float:
    checkpoint_recovery = signals.get("checkpoint_recovery_score", 0.0)
    identity_stability = signals.get("identity_stability", 0.0)
    replay_consistency = signals.get("replay_consistency", 0.0)
    return clamp01(
        (checkpoint_recovery + identity_stability + replay_consistency) / 3.0
    )
