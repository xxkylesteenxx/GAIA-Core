from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping, Sequence


class SourceTier(StrEnum):
    AUTHORITATIVE = "authoritative"
    COMMUNITY = "community"
    EDGE_LOCAL = "edge_local"
    DERIVED = "derived"


@dataclass(slots=True, frozen=True)
class ProvenanceRecord:
    schema_version: str = "1.0"
    provider: str = ""
    provider_record_id: str = ""
    source_tier: SourceTier = SourceTier.AUTHORITATIVE

    source_url: str | None = None
    license: str | None = None
    raw_object_ref: str | None = None
    content_hash: str | None = None

    ingested_at: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class ObservationEnvelope:
    schema_version: str = "1.0"
    observation_id: str = ""

    domain: str = ""         # atmosphere | water | land | biology
    signal_type: str = ""    # alert | timeseries | occurrence | station_status | taxonomy

    observed_at: datetime | None = None
    lat: float | None = None
    lon: float | None = None
    alt_m: float | None = None

    value: Mapping[str, Any] = field(default_factory=dict)
    units: Mapping[str, str] = field(default_factory=dict)
    quality: Mapping[str, Any] = field(default_factory=dict)

    provenance: Sequence[ProvenanceRecord] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)
