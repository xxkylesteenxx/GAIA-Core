"""Pydantic observation schemas for all Earth-system connectors."""
from __future__ import annotations

import enum
import time
from typing import Any

try:
    from pydantic import BaseModel, Field  # type: ignore
except ImportError:  # pragma: no cover
    raise ImportError("pydantic is required. Run: pip install pydantic")


class SourceTaxonomy(str, enum.Enum):
    ATMOSPHERE = "atmosphere"    # NOAA
    GEOSPHERE = "geosphere"      # USGS
    BIOSPHERE = "biosphere"      # GBIF, iNaturalist
    HYDROSPHERE = "hydrosphere"  # USGS streamflow


class ObservationEvent(BaseModel):
    """Canonical observation event published to GAIA.OBSERVATION stream."""
    source: str
    source_taxonomy: SourceTaxonomy
    location_lat: float | None = None
    location_lon: float | None = None
    timestamp_ns: int = Field(default_factory=lambda: time.time_ns())
    freshness_ttl_s: int = 3600
    payload: dict[str, Any]
    raw_url: str | None = None
    quality_score: float = 1.0   # 0.0–1.0; flagged if < 0.5
