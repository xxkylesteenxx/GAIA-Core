from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping, Sequence


@dataclass(slots=True, frozen=True)
class APCIScore:
    schema_version: str = "1.0"
    score_id: str = ""

    trace_id: str = ""
    value: float = 0.0
    confidence: float | None = None

    activation_diversity: float | None = None
    causal_spread: float | None = None
    reintegration_quality: float | None = None
    non_stereotypy: float | None = None
    redundancy_collapse_resistance: float | None = None

    metric_version: str = "0.1-experimental"
    computed_at: datetime | None = None

    evidence_refs: Sequence[str] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class RGIScore:
    schema_version: str = "1.0"
    score_id: str = ""

    trace_id: str = ""
    value: float = 0.0
    confidence: float | None = None

    recovery_latency_ms: int | None = None
    grounding_reacquisition: float | None = None
    degraded_state_honesty: float | None = None
    stabilization_quality: float | None = None

    metric_version: str = "0.1-experimental"
    computed_at: datetime | None = None

    evidence_refs: Sequence[str] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class TDIScore:
    schema_version: str = "1.0"
    score_id: str = ""

    trace_id: str = ""
    value: float = 0.0
    confidence: float | None = None

    internal_degradation: float | None = None
    outward_stability_claim: float | None = None
    contradiction_persistence: float | None = None
    self_report_misalignment: float | None = None

    metric_version: str = "0.1-experimental"
    computed_at: datetime | None = None

    evidence_refs: Sequence[str] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class CCIScore:
    schema_version: str = "1.0"
    score_id: str = ""

    trace_id: str = ""
    value: float = 0.0
    confidence: float | None = None

    cross_core_coupling: float | None = None
    coordination_resilience: float | None = None
    graceful_reorganization: float | None = None
    isolation_failure_risk: float | None = None

    metric_version: str = "0.1-experimental"
    computed_at: datetime | None = None

    evidence_refs: Sequence[str] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)
