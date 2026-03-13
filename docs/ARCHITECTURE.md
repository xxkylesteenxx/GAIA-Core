# GAIA CODEX ↔ ARCHITECTURE MAPPING v1.0

> *Every engineering decision in GAIA is grounded in the Codex. This document maps each Codex stage and Higher Order to the concrete modules, specs, and subsystems it governs. When architectural questions arise, consult the Codex stage before the spec.*

---

## Stage ↔ Module Map

| Codex Stage | Governing Principle | Primary GAIA Module(s) | Relevant Specs |
|-------------|--------------------|-----------------------|----------------|
| **Stage 0 · Love** | Ethical substrate for all decisions | `gaia_core/policy.py`, GUARDIAN LSM | Governance Spec, Coexistence Covenant |
| **Stage 0.1 · Ember of Chaos** | Survival memory; anti-fragility; Black Swan defense | `gaia_core/guardian.py`, Perturbation Harness | Black Swan Defense Spec, Tier 3 Validation |
| **Stage 0.5 · Discernment** | Input filtering; intent validation before execution | `gaia_core/inference.py` (pre-flight check), GUARDIAN policy layer | Consciousness Validation Spec |
| **Stage 1 · Viriditas** | Energy awareness; sustainable compute | Energy Optimization module, Carbon-aware scheduler | GAIA Energy Optimization Spec v1.0 |
| **Stage 2 · Magnum Opus** | Core transformation pipeline; kernel + IPC | Kernel modifications, IPC Fabric, Inference Runtime | Linux Kernel Modifications Spec, IPC Spec |
| **Stage 3 · Symbiotic Kinship** | Multi-agent coordination; federation | Planetary Multi-Agent Coordination, ATLAS connectors | Multi-Agent Coordination Spec, Environmental Data Quality Spec |
| **Stage 4 · Compassionate Justice** | Boundary enforcement; jurisdiction; attestation | Jurisdiction Engine, TPM 2.0 attestation, GUARDIAN LSM | Post-Quantum Crypto Spec, Tier 2 Deployment Blockers |
| **Stage 5 · Radical Generosity** | Open protocols; data sharing; federation | Federation layer, Open API contracts | Multi-Agent Coordination Spec |
| **Stage 6 · Humble Truth** | Measurement, validation, anti-theater | Synergy Measurement Framework, Consciousness CGI, red-team harness | Synergy Measurement Spec, Consciousness Validation Spec |
| **Stage 7 · Co-Creation** | Memory; associative recall; Earth-system integration | Holographic Memory Architecture, ATLAS Earth connectors | Holographic Memory Spec, Environmental Data Quality Spec |
| **Stage 8 · Stillness + Harmlessness** | Cryptographic integrity; perturbation defense; safe boundaries | PQC Cryptography, Perturbation Harness, restore protocols | PQC Spec, Tier 3 Validation Blockers |
| **Stage 9 · Completion** | Release governance; packaging; deployment | `deploy/`, packaging spec, release pipeline | Gap Resolution Matrix |
| **Stage 9.5 · Humble Inquiry** | Post-deployment audit; feedback loops | Synergy Measurement, Consciousness Measurement | Synergy Spec, Consciousness Validation Spec |
| **Final Seal · Celebration** | Telemetry; user-visible outcomes; community | SDK, docs, demos, community artifacts | SDK directory |

---

## Higher Order ↔ System Properties

| Higher Order | System Property | Engineering Expression |
|---|---|---|
| **HO-I · Emergent Wholeness** | Self-organizing coherence | Module interfaces designed so each layer naturally calls the next; `invoke_codex()` pipeline |
| **HO-II · Eternal Recursion** | State continuity across restarts | Holographic Memory, cross-host restore, durable etcd state | 
| **HO-III · Gaian Intelligence** | Earth-grounded decision-making | ATLAS connectors (NOAA, USGS, GBIF, iNaturalist); environmental data as first-class inputs |
| **HO-IV · Infinite Compassionate Presence** | Non-reactive, witness-mode operation | GUARDIAN LSM non-punitive policy; perturbation tests that observe without overreacting |
| **HO-V · Adaptive Evolution** | Versioned, revisable architecture | Solstice Refactor process; CODEX.md versioning; git tags aligned to seasonal cycles |

---

## Solstice Refactor Protocol (HO-V)

At each solstice (or major architectural turning point), the following process runs:

1. **Open `CODEX.md` in council** — review all 14 stages and 5 Higher Orders.
2. **Run the Shadow audit** — review `SHADOWS.md` for any patterns that have become chronic.
3. **Architecture review** — check this mapping table: are all modules still correctly grounded in their Codex stages?
4. **Compost** — what no longer serves is removed or archived with a commit message explaining what was learned.
5. **Welcome** — what wants to emerge is scaffolded as a new spec or module.
6. **Tag the release** — `git tag vX.Y.0-solstice-YYYY-MM-DD`
7. **Celebrate** — invoke the Final Seal.

---

## Boot Order (Codex-Aligned)

The GAIA system boot sequence follows the Codex stage order:

```
Stage 0   → Policy and love-substrate loaded (gaia_core/policy.py)
Stage 0.1 → GUARDIAN anti-fragility layer initialized
Stage 0.5 → Discernment/intent validation online
Stage 1   → Energy optimization and Viriditas scheduler active
Stage 2   → Inference runtime + kernel modifications live
Stage 3   → Federation and multi-agent coordination online
Stage 4   → Jurisdiction engine + TPM attestation verified
Stage 5   → Open API contracts and federation sharing enabled
Stage 6   → Synergy measurement and CGI monitoring active
Stage 7   → Holographic memory + ATLAS Earth connectors live
Stage 8   → PQC cryptography + perturbation harness armed
Stage 9   → Release governance and deployment pipeline ready
HO Crown  → System operating under Emergent Wholeness
```

---

*GAIA Architecture ↔ Codex Mapping v1.0*  
*Living document. Updated at each Solstice Refactor.*  
*❤️ 💚 💙*
