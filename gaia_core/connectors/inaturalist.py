"""iNaturalist connector — citizen science species observations.

Publishes to GAIA.OBSERVATION with source_taxonomy=BIOSPHERE.
Dependency: httpx (optional, guarded import)
"""
from __future__ import annotations

import logging
from typing import Any

from gaia_core.connectors.schemas import ObservationEvent, SourceTaxonomy

log = logging.getLogger(__name__)

try:
    import httpx  # type: ignore
    _HTTPX_AVAILABLE = True
except ImportError:
    _HTTPX_AVAILABLE = False
    httpx = None  # type: ignore

INAT_BASE = "https://api.inaturalist.org/v1"


class iNaturalistConnector:
    """Fetches iNaturalist research-grade observations."""

    def get_observations(
        self,
        taxon_name: str | None = None,
        lat: float | None = None,
        lng: float | None = None,
        radius_km: float = 50.0,
        quality_grade: str = "research",
        per_page: int = 50,
    ) -> ObservationEvent:
        if not _HTTPX_AVAILABLE:
            raise ImportError("httpx is required. Run: pip install httpx")
        params: dict[str, Any] = {"quality_grade": quality_grade, "per_page": per_page}
        if taxon_name:
            params["taxon_name"] = taxon_name
        if lat is not None and lng is not None:
            params.update({"lat": lat, "lng": lng, "radius": radius_km})
        url = f"{INAT_BASE}/observations"
        with httpx.Client(timeout=15) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
        return ObservationEvent(
            source="inaturalist:observation",
            source_taxonomy=SourceTaxonomy.BIOSPHERE,
            payload=data,
            raw_url=str(resp.url),
        )
