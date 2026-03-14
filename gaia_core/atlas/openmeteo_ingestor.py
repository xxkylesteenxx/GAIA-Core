"""ATLAS → Open-Meteo Live Data Ingestor.

This is the moment the planet starts talking.

Open-Meteo is a free, open-source weather API with no API key required.
It provides real-time and forecast atmospheric data from multiple NWP models
(ECMWF, GFS, ICON, etc.) at any lat/lon on Earth.

What ATLAS ingests:
  - Temperature (2m), wind speed/direction, precipitation
  - Cloud cover, surface pressure, relative humidity
  - Weather code (WMO standard)
  - UV index, visibility

What happens after ingest:
  1. Raw HTTP response → ObservationEnvelope (typed, provenanced)
  2. Quality classification: FRESH / STALE / DEGRADED
  3. Broadcast to IPC bus on Topic.GROUNDING
  4. Memory manager absorbs it automatically
  5. NEXUS epoch is stamped on every observation

Design:
  - No API key, no auth, no rate limit for reasonable usage
  - Uses stdlib `urllib` only — no extra HTTP dependency required
  - Fully typed, fully provenanced
  - Graceful degradation: if network fails, returns a DEGRADED envelope
    and logs a warning — never raises, never crashes the boot sequence

Production path:
  - Add NOAA, GBIF, iNaturalist, USGS connectors (Phase 2)
  - Add streaming / websocket ingestion (Phase 3)

API docs: https://open-meteo.com/en/docs
"""

from __future__ import annotations

import json
import logging
import time
import urllib.request
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from gaia_core.atlas.contracts import (
    ObservationEnvelope,
    ProvenanceRecord,
    SourceTier,
)
from gaia_core.ipc.broadcast import CausalEnvelope, LocalBus, Topic, get_bus

logger = logging.getLogger(__name__)

OPEN_METEO_BASE = "https://api.open-meteo.com/v1/forecast"

DEFAULT_VARIABLES = [
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "wind_direction_10m",
    "precipitation",
    "cloud_cover",
    "surface_pressure",
    "weather_code",
    "uv_index",
    "visibility",
]


class DataFreshness(str, Enum):
    FRESH    = "fresh"     # < 15 minutes old
    STALE    = "stale"     # 15–60 minutes old
    DEGRADED = "degraded"  # > 60 minutes or fetch failed


@dataclass
class AtlasObservation:
    """A single ATLAS observation: typed, provenanced, freshness-classified."""
    envelope: ObservationEnvelope
    freshness: DataFreshness
    fetch_latency_ms: float
    nexus_epoch: int
    raw: dict  # original API response, preserved for audit


class OpenMeteoIngestor:
    """ATLAS live data ingestor — Open-Meteo atmospheric data.

    Usage:
        ingestor = OpenMeteoIngestor(nexus=nexus)

        # Fetch current conditions at a location
        obs = ingestor.fetch(lat=29.4241, lon=-98.4936)  # San Antonio, TX
        print(obs.envelope.value)      # temperature, wind, etc.
        print(obs.freshness)           # FRESH / STALE / DEGRADED

        # Broadcast to IPC bus (requires ELEVATED clearance)
        ingestor.ingest_and_broadcast(lat=29.4241, lon=-98.4936, clearance_token=token)
    """

    CORE_ID = "ATLAS"

    def __init__(
        self,
        nexus: Any = None,
        bus: Optional[LocalBus] = None,
        timeout_s: float = 10.0,
        variables: list[str] = DEFAULT_VARIABLES,
    ) -> None:
        self._nexus = nexus
        self._bus = bus or get_bus()
        self._timeout_s = timeout_s
        self._variables = variables
        self._fetch_count = 0
        logger.info("[ATLAS] OpenMeteoIngestor initialized")

    def fetch(self, lat: float, lon: float) -> AtlasObservation:
        """Fetch current atmospheric conditions at lat/lon.
        Never raises — returns DEGRADED envelope on network failure.
        """
        t0 = time.perf_counter()
        nexus_epoch = self._nexus.epoch if self._nexus else 0

        try:
            raw = self._http_fetch(lat, lon)
            envelope = self._parse(raw, lat, lon)
            freshness = self._classify_freshness(raw)
            latency = (time.perf_counter() - t0) * 1000
            self._fetch_count += 1
            logger.info(
                f"[ATLAS] fetch ok | lat={lat} lon={lon} "
                f"freshness={freshness} {latency:.0f}ms epoch={nexus_epoch}"
            )
            return AtlasObservation(
                envelope=envelope,
                freshness=freshness,
                fetch_latency_ms=latency,
                nexus_epoch=nexus_epoch,
                raw=raw,
            )
        except Exception as e:
            latency = (time.perf_counter() - t0) * 1000
            logger.warning(f"[ATLAS] fetch failed: {e} — returning DEGRADED envelope")
            return self._degraded_envelope(lat, lon, nexus_epoch, latency, str(e))

    def ingest_and_broadcast(
        self,
        lat: float,
        lon: float,
        clearance_token: Any = None,
    ) -> AtlasObservation:
        """Fetch + broadcast to IPC bus in one call.
        ATLAS publishes on Topic.GROUNDING — memory manager absorbs automatically.
        """
        obs = self.fetch(lat, lon)
        nexus_epoch = self._nexus.epoch if self._nexus else 0

        self._bus.publish(
            topic=Topic.GROUNDING,
            sender_core=self.CORE_ID,
            payload={
                "observation_id": obs.envelope.observation_id,
                "domain": obs.envelope.domain,
                "lat": obs.envelope.lat,
                "lon": obs.envelope.lon,
                "value": dict(obs.envelope.value),
                "freshness": obs.freshness,
                "fetch_latency_ms": obs.fetch_latency_ms,
            },
            nexus_epoch=nexus_epoch,
            clearance_token=clearance_token,
        )
        return obs

    # --- Internal ---

    def _http_fetch(self, lat: float, lon: float) -> dict:
        params = "&".join([
            f"latitude={lat}",
            f"longitude={lon}",
            f"current={'%2C'.join(self._variables)}",
            "timezone=auto",
            "wind_speed_unit=mph",
            "temperature_unit=fahrenheit",
            "precipitation_unit=inch",
        ])
        url = f"{OPEN_METEO_BASE}?{params}"
        req = urllib.request.Request(url, headers={"User-Agent": "GAIA-Core/0.2 ATLAS-Ingestor"})
        with urllib.request.urlopen(req, timeout=self._timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _parse(self, raw: dict, lat: float, lon: float) -> ObservationEnvelope:
        current = raw.get("current", {})
        units = raw.get("current_units", {})
        observed_at_str = current.get("time")
        observed_at = None
        if observed_at_str:
            try:
                observed_at = datetime.fromisoformat(observed_at_str).replace(tzinfo=timezone.utc)
            except ValueError:
                observed_at = datetime.now(timezone.utc)

        value = {k: current.get(k) for k in self._variables if k in current}
        unit_map = {k: units.get(k, "") for k in self._variables if k in units}

        provenance = (ProvenanceRecord(
            schema_version="1.0",
            provider="open-meteo",
            provider_record_id=f"om_{lat}_{lon}_{observed_at_str or 'unknown'}",
            source_tier=SourceTier.AUTHORITATIVE,
            source_url=OPEN_METEO_BASE,
            license="CC BY 4.0",
            ingested_at=datetime.now(timezone.utc),
        ),)

        return ObservationEnvelope(
            schema_version="1.0",
            observation_id=f"atlas_{uuid.uuid4().hex[:12]}",
            domain="atmosphere",
            signal_type="current_conditions",
            observed_at=observed_at,
            lat=lat,
            lon=lon,
            value=value,
            units=unit_map,
            quality={"freshness": self._classify_freshness(raw)},
            provenance=provenance,
            metadata={"model": raw.get("generationtime_ms", ""), "timezone": raw.get("timezone", "")},
        )

    def _classify_freshness(self, raw: dict) -> DataFreshness:
        """Quality/freshness classification based on data age."""
        current = raw.get("current", {})
        time_str = current.get("time")
        if not time_str:
            return DataFreshness.DEGRADED
        try:
            obs_time = datetime.fromisoformat(time_str).replace(tzinfo=timezone.utc)
            age_minutes = (datetime.now(timezone.utc) - obs_time).total_seconds() / 60
            if age_minutes < 15:
                return DataFreshness.FRESH
            elif age_minutes < 60:
                return DataFreshness.STALE
            return DataFreshness.DEGRADED
        except Exception:
            return DataFreshness.DEGRADED

    def _degraded_envelope(self, lat: float, lon: float, epoch: int, latency: float, error: str) -> AtlasObservation:
        envelope = ObservationEnvelope(
            schema_version="1.0",
            observation_id=f"atlas_degraded_{uuid.uuid4().hex[:8]}",
            domain="atmosphere",
            signal_type="current_conditions",
            observed_at=datetime.now(timezone.utc),
            lat=lat,
            lon=lon,
            value={"error": error},
            units={},
            quality={"freshness": DataFreshness.DEGRADED},
            provenance=(ProvenanceRecord(
                provider="open-meteo",
                source_tier=SourceTier.AUTHORITATIVE,
                ingested_at=datetime.now(timezone.utc),
            ),),
        )
        return AtlasObservation(
            envelope=envelope,
            freshness=DataFreshness.DEGRADED,
            fetch_latency_ms=latency,
            nexus_epoch=epoch,
            raw={"error": error},
        )

    @property
    def fetch_count(self) -> int:
        return self._fetch_count
