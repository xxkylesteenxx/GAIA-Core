from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping, Sequence


class PeerTrustState(StrEnum):
    UNTRUSTED = "untrusted"
    IDENTIFIED = "identified"
    ATTESTED = "attested"
    FEDERATED = "federated"
    DEGRADED = "degraded"
    QUARANTINED = "quarantined"


@dataclass(slots=True, frozen=True)
class MergePrecondition:
    schema_version: str = "1.0"
    precondition_id: str = ""

    requires_attestation: bool = True
    min_peer_trust_state: PeerTrustState = PeerTrustState.ATTESTED

    required_policy_refs: Sequence[str] = field(default_factory=tuple)
    required_quorum_refs: Sequence[str] = field(default_factory=tuple)
    required_capabilities: Sequence[str] = field(default_factory=tuple)

    restore_clean: bool = True
    dissent_ledger_present: bool = True

    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class FederationEnvelope:
    schema_version: str = "1.0"
    message_id: str = ""

    message_type: str = ""        # peer_hello | checkpoint_advert | merge_proposal | dissent_delta
    source_node_id: str = ""
    source_instance_id: str = ""

    source_spiffe_id: str | None = None
    destination_node_id: str | None = None

    peer_trust_state: PeerTrustState = PeerTrustState.UNTRUSTED
    correlation_id: str | None = None
    causation_id: str | None = None

    sent_at: datetime | None = None
    ttl_seconds: int | None = None

    payload: Mapping[str, Any] = field(default_factory=dict)
    payload_hash: str | None = None

    attestation_ref: str | None = None
    signature_ref: str | None = None
    preconditions: Sequence[MergePrecondition] = field(default_factory=tuple)

    metadata: Mapping[str, Any] = field(default_factory=dict)
