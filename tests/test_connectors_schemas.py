"""Unit tests for gaia_core.connectors.schemas."""
import pytest
from gaia_core.connectors.schemas import ObservationEvent, SourceTaxonomy


def test_observation_event_defaults():
    event = ObservationEvent(
        source="noaa:station:KSAT",
        source_taxonomy=SourceTaxonomy.ATMOSPHERE,
        payload={"temperature": 22.5},
    )
    assert event.freshness_ttl_s == 3600
    assert event.quality_score == 1.0
    assert event.timestamp_ns > 0


def test_observation_event_taxonomy_values():
    assert SourceTaxonomy.ATMOSPHERE == "atmosphere"
    assert SourceTaxonomy.GEOSPHERE == "geosphere"
    assert SourceTaxonomy.BIOSPHERE == "biosphere"
    assert SourceTaxonomy.HYDROSPHERE == "hydrosphere"


def test_observation_event_with_location():
    event = ObservationEvent(
        source="usgs:streamflow:08178000",
        source_taxonomy=SourceTaxonomy.HYDROSPHERE,
        location_lat=29.4241,
        location_lon=-98.4936,
        payload={"discharge_cfs": 150.0},
    )
    assert event.location_lat == pytest.approx(29.4241)
    assert event.location_lon == pytest.approx(-98.4936)


def test_observation_event_quality_flag():
    event = ObservationEvent(
        source="inaturalist:observation",
        source_taxonomy=SourceTaxonomy.BIOSPHERE,
        payload={},
        quality_score=0.3,
    )
    assert event.quality_score < 0.5  # Should be flagged
