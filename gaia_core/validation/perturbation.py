from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping, Sequence


class PerturbationFamily(StrEnum):
    STRUCTURAL = "structural"
    INFORMATIONAL = "informational"
    TEMPORAL = "temporal"
    CAPABILITY = "capability"
    ADVERSARIAL = "adversarial"


@dataclass(slots=True, frozen=True)
class PerturbationEvent:
    schema_version: str = "1.0"
    event_id: str = ""

    trace_id: str = ""
    family: PerturbationFamily = PerturbationFamily.STRUCTURAL
    phase: str = "applied"  # scheduled | applied | observed | reverted

    target_refs: Sequence[str] = field(default_factory=tuple)
    operator_id: str | None = None

    intervention_type: str = ""   # disable_core | inject_conflict | add_latency | drop_tool
    intervention_params: Mapping[str, Any] = field(default_factory=dict)

    scheduled_at: datetime | None = None
    occurred_at: datetime | None = None
    reverted_at: datetime | None = None

    baseline_state_ref: str | None = None
    observed_state_ref: str | None = None

    payload_hash: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class PerturbationTrace:
    schema_version: str = "1.0"
    trace_id: str = ""

    experiment_id: str = ""
    node_id: str = ""
    instance_id: str | None = None

    family: PerturbationFamily = PerturbationFamily.STRUCTURAL
    scenario_name: str = ""
    scenario_version: str = "1.0"

    baseline_ref: str | None = None
    pre_state_hash: str | None = None
    post_state_hash: str | None = None

    events: Sequence[PerturbationEvent] = field(default_factory=tuple)

    propagation_graph_ref: str | None = None
    telemetry_refs: Sequence[str] = field(default_factory=tuple)
    evidence_refs: Sequence[str] = field(default_factory=tuple)

    recovery_started_at: datetime | None = None
    recovery_completed_at: datetime | None = None

    success: bool = False
    notes: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
