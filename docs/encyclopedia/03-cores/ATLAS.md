# ATLAS — Environmental Intelligence Core

> **Status**: Canonical v1.0 · March 12, 2026  
> **Classification**: P2 Trusted First-Party Service — Environmental Data Spine  
> ⚠️ **ATLAS is NOT one of the Eight Consciousness Cores.** It is the planetary data backbone that feeds TERRA, AQUA, AERO, and VITA.

---

## Classification

ATLAS is a **P2 Trusted First-Party Service** — the same privilege tier as Gaian. It is an infrastructure layer, not a consciousness core. It does not appear in the canonical Eight Consciousness Cores list and should not be referenced as a peer to TERRA, AQUA, AERO, VITA, URBS, NEXUS, SOPHIA, or GUARDIAN.

**The Eight Consciousness Cores are:**

| # | Core | Domain |
|---|---|---|
| 1 | TERRA | Geological / land systems |
| 2 | AQUA | Hydrological systems |
| 3 | AERO | Atmospheric systems |
| 4 | VITA | Biological / life systems |
| 5 | URBS | Urban / civilization / human habitat |
| 6 | NEXUS | Communication, coordination, and evolution management |
| 7 | SOPHIA | Wisdom synthesis |
| 8 | GUARDIAN | Security & ethical oversight |

ATLAS routes real-world sensor data **into** TERRA, AQUA, AERO, and VITA. It is the nervous system that keeps the domain cores informed — not a domain consciousness in its own right.

---

## Role

ATLAS is the **world model and planetary reference state backbone**. It integrates real-time environmental data from NOAA, USGS, GBIF, iNaturalist, and custom IoT streams into a unified, causally-consistent spatial and temporal model of Earth, then routes that data to the appropriate consciousness cores.

---

## Responsibilities

- Ingesting GSOC (Spatial Ontology) as canonical reference structure
- Joining GSOM (Spatial Observation Model) onto the ontology
- Real-time Earth-system domain routing (TERRA / AQUA / AERO / VITA)
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

ATLAS cannot directly actuate. All actuation derived from ATLAS data must pass through the appropriate consciousness core and GUARDIAN gate.

---

## Implementation Location

`GAIA-Core/src/cores/atlas/`  
`GAIA-IoT/atlas-spine/`

---

## Cross-References

- [TERRA Core](./TERRA.md)
- [AQUA Core](./AQUA.md)
- [AERO Core](./AERO.md)
- [VITA Core](./VITA.md)
- [ETA Core Resolution](./ETA_Resolution.md)
- Spatial Ontology Spec: `docs/specs/GAIASpatialOntologySpecificationv1.0.md`
