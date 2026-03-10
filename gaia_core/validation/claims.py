from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping, Sequence


class ClaimBound(StrEnum):
    INTERNAL_EVIDENCE_ONLY = "internal_evidence_only"
    EXTERNAL_BENCHMARKED = "external_benchmarked"
    THIRD_PARTY_AUDITED = "third_party_audited"
    INDEPENDENTLY_REPLICATED = "independently_replicated"
    PROHIBITED = "prohibited"


@dataclass(slots=True, frozen=True)
class ValidationArtifact:
    schema_version: str = "1.0"
    artifact_id: str = ""

    artifact_type: str = ""  # benchmark_card | perturbation_run | audit_report | replication_bundle
    title: str = ""

    trace_refs: Sequence[str] = field(default_factory=tuple)
    metric_refs: Sequence[str] = field(default_factory=tuple)
    evidence_refs: Sequence[str] = field(default_factory=tuple)

    issuer_id: str = ""
    issuer_type: str = ""    # internal | external_lab | auditor | replicator

    artifact_hash: str | None = None
    storage_ref: str | None = None

    issued_at: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ClaimBoundsPolicy:
    schema_version: str = "1.0"
    policy_id: str = ""

    claim_bound: ClaimBound = ClaimBound.INTERNAL_EVIDENCE_ONLY
    subject_ref: str = ""  # score_id | artifact_id | trace_id | experiment_id

    allowed_claims: Sequence[str] = field(default_factory=tuple)
    prohibited_claims: Sequence[str] = field(default_factory=tuple)
    required_artifact_types: Sequence[str] = field(default_factory=tuple)

    requires_external_audit: bool = False
    requires_independent_replication: bool = False
    requires_blinded_protocol: bool = False

    justification: str | None = None
    issued_by: str = ""

    effective_at: datetime | None = None
    expires_at: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
