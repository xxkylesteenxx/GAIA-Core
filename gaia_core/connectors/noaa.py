"""NOAA connector — atmospheric data (weather, climate, NWP model output).

Publishes to GAIA.OBSERVATION with source_taxonomy=ATMOSPHERE.
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

NOAA_BASE = "https://api.weather.gov"


class NOAAConnector:
    """Fetches NOAA weather observations and gridpoint forecasts."""

    def __init__(self, user_agent: str = "GAIA-OS/1.0 (xxkylesteenxx@outlook.com)") -> None:
        if not _HTTPX_AVAILABLE:
            raise ImportError("httpx is required. Run: pip install httpx")
        self._headers = {"User-Agent": user_agent, "Accept": "application/geo+json"}

    def get_observation(self, station_id: str) -> ObservationEvent:
        """Fetch latest observation from a NOAA station."""
        url = f"{NOAA_BASE}/stations/{station_id}/observations/latest"
        with httpx.Client(headers=self._headers, timeout=10) as client:
            resp = client.get(url)
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()
        props = data.get("properties", {})
        geometry = data.get("geometry", {}).get("coordinates", [None, None])
        return ObservationEvent(
            source=f"noaa:station:{station_id}",
            source_taxonomy=SourceTaxonomy.ATMOSPHERE,
            location_lon=geometry[0],
            location_lat=geometry[1],
            payload=props,
            raw_url=url,
        )
