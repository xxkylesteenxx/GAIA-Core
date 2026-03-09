from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Mapping, MutableMapping, Optional

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class CoreName(str, Enum):
    NEXUS = "NEXUS"
    GUARDIAN = "GUARDIAN"
    ATLAS = "ATLAS"
    SOPHIA = "SOPHIA"
    TERRA = "TERRA"
    AQUA = "AQUA"
    AERO = "AERO"
    VITA = "VITA"

class EvidenceMode(str, Enum):
    INTERNAL = "internal"
    AUDIT = "audit"
    RED_TEAM = "red_team"

class ObservationSourceClass(str, Enum):
    REGULATORY = "S1"
    FIELD = "S2"
    LOW_COST_IOT = "S3"
    REMOTE_SENSING = "S4"
    HUMAN_REPORT = "S5"
    DERIVED = "S6"

@dataclass(slots=True)
class VectorClock:
    versions: Dict[str, int] = field(default_factory=dict)

    def increment(self, actor: str) -> "VectorClock":
        updated = dict(self.versions)
        updated[actor] = updated.get(actor, 0) + 1
        return VectorClock(updated)

    def merge(self, other: "VectorClock") -> "VectorClock":
        merged: Dict[str, int] = dict(self.versions)
        for actor, version in other.versions.items():
            merged[actor] = max(merged.get(actor, 0), version)
        return VectorClock(merged)

    def happened_before(self, other: "VectorClock") -> bool:
        strictly_less = False
        for actor in set(self.versions) | set(other.versions):
            a = self.versions.get(actor, 0)
            b = other.versions.get(actor, 0)
            if a > b:
                return False
            if a < b:
                strictly_less = True
        return strictly_less

@dataclass(slots=True)
class CausalEnvelope:
    emitter: str
    created_at: datetime
    vector_clock: VectorClock
    trace_id: str
    dependencies: List[str] = field(default_factory=list)

@dataclass(slots=True)
class MemoryEvent:
    event_id: str
    core: str
    kind: str
    payload: Dict[str, Any]
    envelope: CausalEnvelope
    tags: List[str] = field(default_factory=list)

@dataclass(slots=True)
class EnvironmentalObservation:
    source_id: str
    domain: str
    observed_at: datetime
    ingest_at: datetime
    payload: Dict[str, Any]
    source_class: ObservationSourceClass
    quality_score: float
    latency_seconds: float
    freshness_class: str
    adversarial_suspicion: float = 0.0

@dataclass(slots=True)
class ConsciousnessEvidence:
    gnwt_score: float
    iit_proxy_score: float
    rpt_score: float
    continuity_score: float
    anti_theater_score: float
    composite_cgi: float
    notes: List[str] = field(default_factory=list)

@dataclass(slots=True)
class DissentRecord:
    core: str
    claim: str
    confidence: float
    rationale: str
    preserved_at: datetime = field(default_factory=utcnow)

@dataclass(slots=True)
class WorkspaceState:
    workspace_id: str
    epoch: int
    problem_frame: str
    goals: List[str]
    commitments: List[str]
    dissent: List[DissentRecord] = field(default_factory=list)
    evidence_refs: List[str] = field(default_factory=list)
    updated_at: datetime = field(default_factory=utcnow)

@dataclass(slots=True)
class CheckpointManifest:
    checkpoint_id: str
    created_at: datetime
    identity_root_fingerprint: str
    registered_cores: List[str]
    event_count: int
    workspace_epoch: int
    notes: List[str] = field(default_factory=list)
