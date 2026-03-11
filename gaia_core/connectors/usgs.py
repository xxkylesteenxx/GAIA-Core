"""USGS connector — geosphere data (seismic, streamflow, groundwater).

Publishes to GAIA.OBSERVATION with source_taxonomy=GEOSPHERE or HYDROSPHERE.
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

USGS_WATER_BASE = "https://waterservices.usgs.gov/nwis"
USGS_EARTHQUAKE_BASE = "https://earthquake.usgs.gov/fdsnws/event/1"


class USGSConnector:
    """Fetches USGS streamflow and earthquake data."""

    def get_streamflow(self, site_no: str, period: str = "P1D") -> ObservationEvent:
        """Fetch latest streamflow for a USGS gauge site."""
        if not _HTTPX_AVAILABLE:
            raise ImportError("httpx is required. Run: pip install httpx")
        url = f"{USGS_WATER_BASE}/iv/?sites={site_no}&period={period}&format=json"
        with httpx.Client(timeout=10) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
        return ObservationEvent(
            source=f"usgs:streamflow:{site_no}",
            source_taxonomy=SourceTaxonomy.HYDROSPHERE,
            payload=data,
            raw_url=url,
        )

    def get_recent_earthquakes(self, min_magnitude: float = 2.5, limit: int = 20) -> ObservationEvent:
        """Fetch recent earthquakes above a magnitude threshold."""
        if not _HTTPX_AVAILABLE:
            raise ImportError("httpx is required. Run: pip install httpx")
        url = f"{USGS_EARTHQUAKE_BASE}/query?format=geojson&minmagnitude={min_magnitude}&limit={limit}"
        with httpx.Client(timeout=10) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
        return ObservationEvent(
            source="usgs:earthquake",
            source_taxonomy=SourceTaxonomy.GEOSPHERE,
            payload=data,
            raw_url=url,
        )
