"""GAIA Earth-system data connectors.

All connectors publish to the GAIA.OBSERVATION JetStream stream via
CausalEvent payloads. Schema validation is enforced via Pydantic models.
"""

from gaia_core.connectors.schemas import ObservationEvent, SourceTaxonomy

__all__ = ["ObservationEvent", "SourceTaxonomy"]
