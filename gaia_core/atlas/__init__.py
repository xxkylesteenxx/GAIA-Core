"""ATLAS — World-Model and Planetary Reference State Core.

ATLAS ingests real-world environmental data and maintains
GAIA's grounded model of the planet's current state.

First live data source: Open-Meteo atmospheric conditions (no API key required).
Next: NOAA, GBIF, iNaturalist, USGS connectors.

Boot order: GUARDIAN-Lite → NEXUS → GUARDIAN-Full → SOPHIA → Domain Cores (incl. ATLAS)

ATLAS does NOT reason about data — that is SOPHIA's domain.
ATLAS does NOT gate ethics — that is GUARDIAN's domain.
ATLAS ingests. That is her gift. The planet speaks; ATLAS listens.
"""

from .openmeteo_ingestor import OpenMeteoIngestor, AtlasObservation, DataFreshness
from .contracts import ObservationEnvelope, ProvenanceRecord, SourceTier

__all__ = [
    "OpenMeteoIngestor",
    "AtlasObservation",
    "DataFreshness",
    "ObservationEnvelope",
    "ProvenanceRecord",
    "SourceTier",
]
__version__ = "0.1.0"
