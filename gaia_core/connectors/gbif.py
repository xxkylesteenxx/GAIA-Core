"""GBIF connector — biodiversity species occurrence data.

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

GBIF_BASE = "https://api.gbif.org/v1"


class GBIFConnector:
    """Fetches GBIF species occurrence records."""

    def search_occurrences(
        self,
        taxon_key: int | None = None,
        country: str | None = None,
        limit: int = 50,
    ) -> ObservationEvent:
        if not _HTTPX_AVAILABLE:
            raise ImportError("httpx is required. Run: pip install httpx")
        params: dict[str, Any] = {"limit": limit}
        if taxon_key:
            params["taxonKey"] = taxon_key
        if country:
            params["country"] = country
        url = f"{GBIF_BASE}/occurrence/search"
        with httpx.Client(timeout=15) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
        return ObservationEvent(
            source="gbif:occurrence",
            source_taxonomy=SourceTaxonomy.BIOSPHERE,
            payload=data,
            raw_url=str(resp.url),
        )
