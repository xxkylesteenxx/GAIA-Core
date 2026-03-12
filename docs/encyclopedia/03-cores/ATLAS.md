# ATLAS — Environmental Intelligence Core

> **Part III — The Eight Consciousness Cores**  
> **Status**: Canonical v1.0 · March 12, 2026

---

## Role

ATLAS is the **world model and planetary reference state core**. It integrates real-time environmental data from NOAA, USGS, GBIF, iNaturalist, and custom IoT streams into a unified, causally-consistent spatial and temporal model of Earth.

---

## Responsibilities

- Ingesting GSOC (Spatial Ontology) as canonical reference structure
- Joining GSOM (Spatial Observation Model) onto the ontology
- Real-time Earth-system domain routing (TERRA/AQUA/AERO/VITA)
- Environmental data quality scoring and freshness management
- ATLAS Data Spine (IoT integration backbone)
- Geospatial awareness and scale reasoning
- Adversarial robustness on sensor inputs
- Carbon-aware scheduling data provider

---

## Data Sources

| Source | Domain | Latency Class |
|--------|---------|---------------|
| NOAA APIs | AERO (atmosphere) | Near-real-time |
| USGS Earthquake API | TERRA (land) | Real-time |
| GBIF/iNaturalist | VITA (biological) | Batch/streaming |
| Custom IoT sensors | All domains | Real-time |

---

## Privilege Class

**P2 — Trusted First-Party Service**

---

## Implementation Location

`GAIA-Core/src/cores/atlas/`  
`GAIA-IoT/atlas-spine/`
