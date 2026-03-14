"""Tests for ATLAS Open-Meteo ingestor.

Covers:
  - Fetch returns an AtlasObservation (no network: mock urllib)
  - Observation has valid ObservationEnvelope shape
  - Provenance records Open-Meteo as provider with CC BY 4.0 license
  - Freshness classification: FRESH / STALE / DEGRADED
  - Network failure returns DEGRADED envelope, never raises
  - ingest_and_broadcast publishes to IPC bus
  - fetch_count increments on each successful fetch
  - Domain is always 'atmosphere'
"""

from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

import pytest

from gaia_core.atlas.openmeteo_ingestor import (
    AtlasObservation,
    DataFreshness,
    OpenMeteoIngestor,
)
from gaia_core.ipc.broadcast import LocalBus, Topic, reset_bus


# Minimal realistic Open-Meteo API response
def _mock_response(age_minutes: float = 0) -> dict:
    obs_time = datetime.now(timezone.utc) - timedelta(minutes=age_minutes)
    return {
        "latitude": 29.4241,
        "longitude": -98.4936,
        "timezone": "America/Chicago",
        "generationtime_ms": 0.21,
        "current_units": {
            "temperature_2m": "°F",
            "wind_speed_10m": "mph",
            "relative_humidity_2m": "%",
            "precipitation": "inch",
            "weather_code": "wmo code",
        },
        "current": {
            "time": obs_time.strftime("%Y-%m-%dT%H:%M"),
            "temperature_2m": 68.4,
            "wind_speed_10m": 10.2,
            "relative_humidity_2m": 65,
            "precipitation": 0.0,
            "weather_code": 1,
        },
    }


@pytest.fixture(autouse=True)
def fresh_bus():
    reset_bus()
    yield
    reset_bus()


class TestOpenMeteoIngestor:
    def _patched_ingestor(self, age_minutes=0):
        """Return an ingestor that uses a mocked HTTP response."""
        ingestor = OpenMeteoIngestor()
        ingestor._http_fetch = MagicMock(return_value=_mock_response(age_minutes))
        return ingestor

    def test_fetch_returns_atlas_observation(self):
        ingestor = self._patched_ingestor()
        obs = ingestor.fetch(lat=29.4241, lon=-98.4936)
        assert isinstance(obs, AtlasObservation)

    def test_envelope_domain_is_atmosphere(self):
        ingestor = self._patched_ingestor()
        obs = ingestor.fetch(lat=29.4241, lon=-98.4936)
        assert obs.envelope.domain == "atmosphere"

    def test_envelope_has_temperature(self):
        ingestor = self._patched_ingestor()
        obs = ingestor.fetch(lat=29.4241, lon=-98.4936)
        assert "temperature_2m" in obs.envelope.value
        assert obs.envelope.value["temperature_2m"] == 68.4

    def test_provenance_records_open_meteo(self):
        ingestor = self._patched_ingestor()
        obs = ingestor.fetch(lat=29.4241, lon=-98.4936)
        assert len(obs.envelope.provenance) > 0
        assert obs.envelope.provenance[0].provider == "open-meteo"
        assert obs.envelope.provenance[0].license == "CC BY 4.0"

    def test_fresh_data_classified_fresh(self):
        ingestor = self._patched_ingestor(age_minutes=0)
        obs = ingestor.fetch(lat=29.4241, lon=-98.4936)
        assert obs.freshness == DataFreshness.FRESH

    def test_old_data_classified_stale(self):
        ingestor = self._patched_ingestor(age_minutes=30)
        obs = ingestor.fetch(lat=29.4241, lon=-98.4936)
        assert obs.freshness == DataFreshness.STALE

    def test_very_old_data_classified_degraded(self):
        ingestor = self._patched_ingestor(age_minutes=90)
        obs = ingestor.fetch(lat=29.4241, lon=-98.4936)
        assert obs.freshness == DataFreshness.DEGRADED

    def test_network_failure_returns_degraded_never_raises(self):
        ingestor = OpenMeteoIngestor()
        ingestor._http_fetch = MagicMock(side_effect=ConnectionError("network down"))
        obs = ingestor.fetch(lat=0.0, lon=0.0)
        assert obs.freshness == DataFreshness.DEGRADED
        assert "error" in obs.envelope.value

    def test_fetch_count_increments(self):
        ingestor = self._patched_ingestor()
        assert ingestor.fetch_count == 0
        ingestor.fetch(lat=29.4241, lon=-98.4936)
        assert ingestor.fetch_count == 1
        ingestor.fetch(lat=29.4241, lon=-98.4936)
        assert ingestor.fetch_count == 2

    def test_ingest_and_broadcast_publishes_to_bus(self):
        from gaia_core.guardian.nexus_clearance import ClearanceLevel, GuardianNexusClearance
        bus = LocalBus()
        ingestor = OpenMeteoIngestor(bus=bus)
        ingestor._http_fetch = MagicMock(return_value=_mock_response())

        received = []
        bus.subscribe(Topic.GROUNDING, "TEST", received.append)

        guardian = GuardianNexusClearance()
        token = guardian.evaluate(
            system_state={}, context={"requested_level": ClearanceLevel.ELEVATED}
        )
        ingestor.ingest_and_broadcast(lat=29.4241, lon=-98.4936, clearance_token=token)
        assert len(received) == 1
        assert received[0].sender_core == "ATLAS"
        assert received[0].topic == Topic.GROUNDING
