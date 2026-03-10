from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Mapping, Sequence


class TrustClass(StrEnum):
    UNVERIFIED = "unverified"
    DEGRADED = "degraded"
    TRUSTED = "trusted"
    QUARANTINED = "quarantined"


@dataclass(slots=True, frozen=True)
class TPMPresence:
    schema_version: str = "1.0"
    present: bool = False
    simulator: bool = False

    manufacturer: str | None = None
    vendor_string: str | None = None
    firmware_version: str | None = None
    spec_revision: str | None = None

    pcr_banks: Sequence[str] = field(default_factory=tuple)


@dataclass(slots=True, frozen=True)
class AttestationBundle:
    schema_version: str = "1.0"
    node_id: str = ""
    trust_class: TrustClass = TrustClass.UNVERIFIED

    nonce: str = ""
    quote_blob_b64: str = ""
    quote_signature_b64: str = ""
    quote_algorithm: str = ""

    pcr_values: Mapping[str, str] = field(default_factory=dict)
    ak_certificate_chain_pem: Sequence[str] = field(default_factory=tuple)
    event_log_ref: str | None = None

    issued_at: datetime | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)
