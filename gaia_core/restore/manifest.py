from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping, Sequence

from gaia_core.security.tpm.contracts import TrustClass


class RestorePath(StrEnum):
    SOFT_RESTART = "soft_restart"
    SAME_HOST = "same_host"
    CROSS_HOST = "cross_host"
    K8S_STATEFUL_RESTORE = "k8s_stateful_restore"
    CRIU_MIGRATION = "criu_migration"
    QUARANTINED_FOREIGN_HOST = "quarantined_foreign_host"


@dataclass(slots=True, frozen=True)
class TrustStateTransition:
    schema_version: str = "1.0"
    transition_id: str = ""

    node_id: str = ""
    from_state: TrustClass = TrustClass.UNVERIFIED
    to_state: TrustClass = TrustClass.UNVERIFIED

    reason_code: str = ""
    reason_detail: str | None = None

    approved_by: str | None = None
    evidence_refs: Sequence[str] = field(default_factory=tuple)

    occurred_at: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class RestoreManifest:
    schema_version: str = "1.0"
    manifest_id: str = ""

    checkpoint_id: str = ""
    node_id: str = ""
    source_node_id: str | None = None

    restore_path: RestorePath = RestorePath.SOFT_RESTART
    requested_trust_class: TrustClass = TrustClass.UNVERIFIED

    epoch: int = 0
    causal_cursor: str | None = None
    parent_manifest_id: str | None = None

    manifest_hash: str = ""
    state_hash: str = ""
    payload_hash: str = ""

    manifest_uri: str = ""
    payload_uri: str = ""
    event_log_tail_ref: str | None = None

    runtime_versions: Mapping[str, str] = field(default_factory=dict)
    model_versions: Mapping[str, str] = field(default_factory=dict)
    attestation_ref: str | None = None

    admissibility_policy_ref: str | None = None
    split_brain_token: str | None = None

    created_at: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
