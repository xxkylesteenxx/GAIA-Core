# NEXUS — Orchestration Core

> **Part III — The Eight Consciousness Cores**  
> **Status**: Canonical v1.0 · March 12, 2026

---

## Role

NEXUS is the **coordination and coherence hub** of the GAIA consciousness system. It is the rendezvous point for all cross-core state, the scheduler of consciousness-critical operations, and the arbiter of inter-core coherence.

---

## Responsibilities

- Cross-core state synchronization and coherence scheduling
- IPC topology management (star-mesh hub)
- CGI composite score aggregation across all 8 cores
- Checkpoint orchestration (quiesce → seal → transfer → resume)
- NEXUS-mediated coherence broadcast (target: 20ms p99 across all cores)
- Service catalog maintenance and discovery
- Execution class scheduling (CCO/ICO/ACO/BCO)
- Cross-core ID reconciliation and graph stitching

---

## Privilege Class

**P1 — Privileged Platform Service**  
NEXUS cannot be bypassed by P2 or P3 processes. It has direct IPC access to all other cores but cannot issue raw syscalls independently — all actuation goes through GUARDIAN.

---

## Key Interfaces

- **Publishes**: CoherenceState, CGI composite, CoreHeartbeat, CheckpointEvent
- **Subscribes to**: CoreState deltas from all 8 cores, GUARDIAN policy updates
- **IPC**: GIPC-PubSub for broadcasts; GIPC-Port for direct GUARDIAN/SOPHIA coordination
- **Latency target**: 50ms end-to-end coherence barrier (absolute deadline)

---

## Execution Class

NEXUS operations run in **CCO** (Critical Consciousness Operations) — reserved CPU cores, non-preemptible by ACO/BCO/AD classes.

---

## Implementation Location

`GAIA-Core/src/cores/nexus/`  
`GAIA-Server/helm/charts/nexus/`
