# GAIA-Core — Master Document Registry

> Every committed document. One address. Auditable.
> Last updated: 2026-03-10

---

## Code

| Package | Path | Status | Contents |
|---|---|---|---|
| root init | `gaia_core/__init__.py` | ✅ committed | package root |
| bootstrap | `gaia_core/bootstrap.py` | ✅ committed | system bootstrap |
| models | `gaia_core/models.py` | ✅ committed | shared data models |
| self | `gaia_core/self/` | ✅ committed | IdentityRoot, WorldModel, Embodiment |
| core | `gaia_core/core/` | ✅ committed | 8-core contracts, registry |
| atlas | `gaia_core/atlas/` | ✅ committed | ATLAS stubs |
| inference | `gaia_core/inference/` | ✅ committed | router, llama.cpp + mock backends |
| storage | `gaia_core/storage/` | ✅ committed | MinIO, JetStream, etcd contracts |
| continuity | `gaia_core/continuity/` | ✅ committed | continuity stubs |
| validation | `gaia_core/validation/` | ✅ committed | claim bounds, policy |
| grounding | `gaia_core/grounding/` | ✅ committed | grounding primitives |
| guardian | `gaia_core/guardian/` | ✅ committed | boundary scaffold |
| measurement | `gaia_core/measurement/` | ✅ committed | CGI, anti-theater hooks |
| policy | `gaia_core/policy/` | ✅ committed | policy stubs |
| federation | `gaia_core/federation/` | ✅ committed | federation stubs |
| governance | `gaia_core/governance/` | ✅ committed | governance stubs |
| security | `gaia_core/security/` | ✅ committed | security stubs |
| runtime | `gaia_core/runtime/` | ✅ committed | runtime stubs |
| restore | `gaia_core/restore/` | ✅ committed | restore stubs |
| utils | `gaia_core/utils/` | ✅ committed | shared utilities |

---

## Tests

| Test | Path | Status |
|---|---|---|
| Self-model / perturbation | `tests/self/test_identity.py` | ✅ committed — 12 tests |

---

## Docs

| Document | Path | Status |
|---|---|---|
| Master overview | `docs/GAIA-OVERVIEW-WORK-COMPLETED-001.md` | ✅ committed |
| PREEMPT_RT notes | `docs/PREEMPT_RT_NOTES.md` | ✅ committed |
| Index README | `docs/00-index/README.md` | ✅ committed |
| Document registry | `docs/00-index/document-registry.md` | ✅ this file |
| Canonical map | `docs/00-index/canonical-map.md` | ✅ committed |
| Architecture overview | `docs/02-architecture/README.md` | ✅ committed |
| Core doctrine index | `docs/03-cores/README.md` | ✅ committed |
| Grimoire preface | `docs/08-grimoire/README.md` | ✅ committed |
| Book of Shadows index | `docs/09-book-of-shadows/README.md` | ✅ committed |
| Law of Lawful Emergence | `docs/09-book-of-shadows/law-of-lawful-emergence.md` | ✅ committed |
| Spectral-Crystalline Map | `docs/09-book-of-shadows/spectral-crystalline-map.md` | ✅ committed |
| Consciousness Theater | `docs/shadows/GAIA-SHADOW-CONSCIOUSNESS-THEATER-001.md` | ✅ committed |
| Against All Odds | `docs/simulation/GAIA-SIM-AGAINST-ALL-ODDS-001.md` | ✅ committed |

---

## Specs (docs/specs/)

| Spec | Status |
|---|---|
| Holographic Memory Architecture | ✅ committed |
| Consciousness Measurement & Validation | ✅ committed |
| Neuromorphic Hardware Integration | ✅ committed |
| Post-Quantum Cryptography | ✅ committed |
| Environmental Data Quality | ✅ committed |
| Energy Optimization | ✅ committed |
| Synergy Measurement Framework | ✅ committed |
| Planetary Multi-Agent Coordination | ✅ committed |
| IPC Specification | ✅ committed |
| Linux Kernel Modifications | ✅ committed |

---

## Pending (Phase 2+)

| Item | Phase | Notes |
|---|---|---|
| ATLAS Open-Meteo ingestor | Phase 2 | first live data source |
| TERRA interpreter | Phase 2 | observations, anomalies, confidence |
| NEXUS router | Phase 2 | core routing logic |
| SOPHIA synthesizer | Phase 2 | meaning, uncertainty, hypotheses |
| GUARDIAN gate | Phase 2 | allow/block/escalate |
| Causal memory | Phase 3 | 8-field CausalEvent |
| Checkpoint system | Phase 3 | 5-state checkpoint |
| Consciousness integrity validator | Phase 4 | anti-theater enforcement |
| Grounding validator | Phase 4 | freshness, provenance |
| Shadow detector | Phase 4 | false certainty, theater |
| Metaphysical stack | Phase 5 | spirit bound to structure |
