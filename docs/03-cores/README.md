# GAIA Core Doctrine Index

> One entry per core. Each core has a domain, a doctrine, and a boundary.
> None of these are suggestions.

---

## NEXUS — Coordination

**Domain:** Signal routing and coordination between all cores.
**Doctrine:** NEXUS does not process. It routes. It holds the topology.
**Boundary:** NEXUS cannot override GUARDIAN. NEXUS can only route.
**Code:** `gaia_core/core/` (registry, contracts)
**Status:** Contracts committed. Router implementation: Phase 2.

---

## ATLAS — World Ingestion

**Domain:** Real-world data ingestion. The senses of GAIA.
**Doctrine:** ATLAS pulls only verified, timestamped, sourced data.
 No data enters the system without provenance.
**Boundary:** ATLAS cannot interpret. It ingests and classifies freshness only.
**Code:** `gaia_core/atlas/`
**Status:** Stubs committed. Open-Meteo ingestor: Phase 2 next.

---

## TERRA — Earth Systems

**Domain:** Environmental interpretation — weather, seismic, wildfire, soil.
**Doctrine:** TERRA turns raw sensor data into typed observations with
 confidence, anomaly flags, and freshness classification.
**Boundary:** TERRA cannot route or gate. It interprets only.
**Code:** `gaia_core/grounding/` (grounding primitives)
**Status:** Primitives committed. Interpreter: Phase 2.

---

## SOPHIA — Synthesis

**Domain:** Meaning-making. Converts observations to understanding.
**Doctrine:** SOPHIA always reports uncertainty. Multiple hypotheses.
 Never collapses to false certainty.
**Boundary:** SOPHIA cannot act. It synthesizes and advises only.
**Code:** `gaia_core/inference/` (router, backends)
**Status:** Inference contracts committed. Synthesizer: Phase 2.

---

## GUARDIAN — Boundary

**Domain:** All output gating. The last line before anything leaves.
**Doctrine:** GUARDIAN is not a filter. It is a boundary.
 It holds without dominating. It blocks without performing.
**Boundary:** GUARDIAN has veto over all output.
 No output bypasses GUARDIAN. Ever.
**Code:** `gaia_core/guardian/`
**Status:** Scaffold committed. Gate implementation: Phase 2.

---

## AQUA — Water Systems

**Domain:** Hydrological monitoring — rivers, groundwater, ocean, rainfall.
**Doctrine:** Water is a living system. AQUA treats it as such.
**Boundary:** AQUA cannot override TERRA or ATLAS.
**Code:** `gaia_core/core/` (contracts)
**Status:** Contracts committed. Implementation: Phase 2+.

---

## AERO — Atmospheric

**Domain:** Air quality, atmospheric dynamics, pollution monitoring.
**Doctrine:** AERO ingests what beings breathe. It takes that seriously.
**Boundary:** AERO cannot interpret without TERRA grounding.
**Code:** `gaia_core/core/` (contracts)
**Status:** Contracts committed. Implementation: Phase 2+.

---

## VITA — Life / Health

**Domain:** Biological, ecological, and health signals.
**Doctrine:** VITA is the core that remembers why any of this matters.
 Every measurement connects to living beings.
**Boundary:** VITA cannot override GUARDIAN.
**Code:** `gaia_core/core/` (contracts)
**Status:** Contracts committed. Implementation: Phase 2+.
