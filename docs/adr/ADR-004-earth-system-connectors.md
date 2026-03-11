# ADR-004: Earth-System Data Connectors

**Status:** Draft  
**Tier:** 1  
**Date:** 2026-03-10  
**GitHub Issue:** TBD

## Context

GAIA's environmental consciousness cores (TERRA, AQUA, AERO, VITA) require live, high-quality Earth-system data to ground their awareness in real planetary state. Without authoritative external data feeds, these cores operate on stale or synthetic inputs, undermining the grounding guarantee.

## Decision

*[To be finalized — stub for tracking]*

Proposed connector targets:

| Source | Domain | Data |
|--------|--------|------|
| NOAA APIs | Atmosphere | Weather, climate, NWP model output |
| USGS | Geosphere | Seismic, streamflow, groundwater, land cover |
| GBIF | Biosphere | Species occurrence, biodiversity observations |
| iNaturalist | Biosphere | Citizen science species observations |

All connectors write to `GAIA.OBSERVATION` JetStream stream (see ADR-002). Schema validation via Pydantic models in `gaia_core/connectors/`.

## Consequences

*TBD — pending latency class and freshness requirements per connector*

## Implementation Tasks

- [ ] `gaia_core/connectors/noaa.py`
- [ ] `gaia_core/connectors/usgs.py`
- [ ] `gaia_core/connectors/gbif.py`
- [ ] `gaia_core/connectors/inaturalist.py`
- [ ] Pydantic observation schemas in `gaia_core/connectors/schemas.py`
- [ ] Freshness / staleness TTL policy per source
- [ ] Backpressure handling when JetStream is slow
