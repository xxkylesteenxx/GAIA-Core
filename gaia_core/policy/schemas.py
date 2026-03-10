from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping, Sequence


class PolicyDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_HUMAN_APPROVAL = "require_human_approval"
    REQUIRE_ADDITIONAL_CONSENT = "require_additional_consent"
    REQUIRE_JURISDICTION_OVERRIDE = "require_jurisdiction_override"
    QUARANTINE = "quarantine"


@dataclass(slots=True, frozen=True)
class PolicyInput:
    schema_version: str = "1.0"
    request_id: str = ""

    actor_id: str = ""
    actor_type: str = ""          # human | gaia_core | workload | external_system
    action: str = ""              # deploy | restore | federate | actuate | merge
    target_id: str = ""
    target_type: str = ""         # node | dataset | policy_bundle | merge_proposal

    jurisdiction_hints: Mapping[str, str] = field(default_factory=dict)
    capability_scope: Sequence[str] = field(default_factory=tuple)

    safety_impact: str = "low"    # low | moderate | high | critical
    risk_factors: Mapping[str, Any] = field(default_factory=dict)

    evidence_refs: Sequence[str] = field(default_factory=tuple)
    context: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class PolicyResult:
    schema_version: str = "1.0"
    request_id: str = ""

    decision: PolicyDecision = PolicyDecision.DENY
    accepted: bool = False

    reason_codes: Sequence[str] = field(default_factory=tuple)
    explanation: str | None = None

    policy_refs: Sequence[str] = field(default_factory=tuple)
    jurisdiction_routes: Sequence[str] = field(default_factory=tuple)

    required_approval_roles: Sequence[str] = field(default_factory=tuple)
    required_consent_scopes: Sequence[str] = field(default_factory=tuple)

    expires_at: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ApprovalArtifact:
    schema_version: str = "1.0"
    artifact_id: str = ""

    request_id: str = ""
    approver_id: str = ""
    approver_role: str = ""

    decision: PolicyDecision = PolicyDecision.DENY
    justification: str | None = None

    authn_method: str = ""        # webauthn | mfa | break_glass
    authn_ref: str | None = None

    scope: Sequence[str] = field(default_factory=tuple)
    jurisdiction: str | None = None

    issued_at: datetime | None = None
    expires_at: datetime | None = None

    evidence_refs: Sequence[str] = field(default_factory=tuple)
    signature_ref: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
