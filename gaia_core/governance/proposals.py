from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping, Sequence


class QuorumClass(StrEnum):
    SIMPLE = "simple"
    SAFETY = "safety"
    FEDERATION = "federation"
    CONSTITUTIONAL = "constitutional"


class MergeDisposition(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    QUARANTINED = "quarantined"
    EXPIRED = "expired"


@dataclass(slots=True, frozen=True)
class DissentReference:
    schema_version: str = "1.0"
    dissent_id: str = ""

    author_id: str = ""
    summary: str = ""

    artifact_ref: str | None = None
    evidence_refs: Sequence[str] = field(default_factory=tuple)

    created_at: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class MergeProposal:
    schema_version: str = "1.0"
    proposal_id: str = ""

    title: str = ""
    summary: str = ""

    proposer_id: str = ""
    proposer_role: str = ""

    parent_state_ref: str = ""
    proposed_state_ref: str = ""

    affected_scopes: Sequence[str] = field(default_factory=tuple)
    jurisdiction_impact_set: Sequence[str] = field(default_factory=tuple)

    quorum_class: QuorumClass = QuorumClass.SIMPLE
    safety_impact: str = "low"    # low | moderate | high | critical

    dissent_refs: Sequence[DissentReference] = field(default_factory=tuple)
    evidence_refs: Sequence[str] = field(default_factory=tuple)
    approval_artifact_refs: Sequence[str] = field(default_factory=tuple)

    final_disposition: MergeDisposition = MergeDisposition.PENDING
    disposition_reason: str | None = None

    created_at: datetime | None = None
    closes_at: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
