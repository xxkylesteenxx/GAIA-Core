# GAIA-Core Critical Path v1.0

- **Document ID:** GAIA-CORE-CRITICAL-PATH-001
- **Version:** v1.0
- **Status:** Draft for Implementation
- **Owner:** GAIA-Core
- **Primary Repo Path:** `docs/02-architecture/gaia-core-critical-path_v1.0.md`
- **Scope:** Kernel foundation, IPC, memory, neuromorphic pilot, energy optimization, and cross-repo propagation
- **Date:** 2026-03-10

---

## Purpose

This document defines the ordered implementation path for GAIA-Core and its downstream distribution repos. It resolves dependency order, phase gates, exit criteria, benchmark thresholds, rollback rules, and immediate deliverables.

This is the canonical execution sequence for turning GAIA from a validated architectural concept into a production-plausible substrate.

---

## Executive Decision

**Build order is kernel-first.**

The dependency chain is:

1. **Real-time kernel substrate**
2. **IPC nervous system**
3. **Holographic memory substrate**
4. **Neuromorphic pilot path**
5. **Energy optimization and distribution-repo inheritance**

Two critical implementation rules govern the whole path:

- **Do not use `sched_ext` / `scx_gaia` as the first proof of timing.** Establish latency on PREEMPT_RT + CPU isolation + IRQ affinity first.
- **Do not assume cgroup v2 alone cleanly solves RT partitioning.** The RT/cgroup caveat must be handled explicitly.

---

## Canonical Dependency Graph

```text
P0A PREEMPT_RT baseline
  -> P0B CPU isolation / IRQ topology / cgroup-v2 + cpuset layout
    -> P0C jitter benchmark harness
      -> P0D GUARDIAN narrow-scope LSM / BPF-LSM
        -> P0E scx_gaia BPF scheduler
          -> P1 IPC transport layer
            -> P2 holographic memory foundation
              -> P3 neuromorphic pilot (AERO first)
                -> P4 energy optimization + distribution-repo propagation
```

---

## Phase 0 — Kernel Foundation (GAIA-Core)

### Why this phase goes first

Without a validated real-time substrate, timing guarantees for IPC, memory ordering, replay determinism, and neuromorphic coordination remain aspirational.

### Phase 0A — PREEMPT_RT baseline

#### Target

- Prefer **Linux 6.12-rt**
- Accept **Linux 6.6-rt** if platform support or driver availability is materially better

#### Required kernel posture

- PREEMPT_RT enabled
- forced threaded interrupts where applicable
- deterministic CPU topology planning
- measurement harness in place before policy experimentation

#### Baseline deliverables

- bootable PREEMPT_RT image
- reproducible kernel config
- benchmark host profile documented
- kernel build recipe captured in repo

#### Exit criteria

- kernel boots reliably on target hardware
- no blocking driver regressions for planned GAIA host
- benchmark harness can collect wakeup latency, IRQ latency, and cross-core coordination timing
- baseline results stored as artifacts

#### Rollback rule

Rollback to the previous known-good RT kernel if:
- required devices fail to initialize
- median latency improves but tail latency regresses beyond target
- driver instability blocks sustained benchmarking

### Phase 0B — CPU isolation, IRQ pinning, and reservation layout

#### Objective

Reserve execution territory for latency-critical cores before introducing custom scheduling.

#### Required layout

- isolate **NEXUS** and **GUARDIAN** CPUs
- pin critical IRQs deliberately
- create cpuset/cgroup structure for:
  - guardian
  - nexus
  - terra
  - aqua
  - aero
  - vita
  - sophia
  - urbs

#### Reservation principle

Use cgroup v2 and cpusets for structural partitioning, but do **not** rely on cgroup v2 CPU control alone for RT workloads.

#### Exit criteria

- documented CPU affinity map
- documented IRQ affinity map
- cpuset hierarchy created and reproducible
- noncritical workloads kept off isolated CPUs

#### Rollback rule

Rollback the affinity plan if:
- IRQ storms collapse isolated cores
- scheduler migration overhead offsets isolation benefit
- key system services become unstable

### Phase 0C — Benchmark harness and timing proof

#### Objective

Prove the kernel substrate before custom scheduler work.

#### Minimum measurements

- wakeup latency
- IRQ handling latency
- cross-core coordination latency for NEXUS↔GUARDIAN hot path
- jitter under representative background load
- memory-write acknowledgment timing for a minimal event path

#### Target thresholds

- **NEXUS coordination target:** sub-10 ms end-to-end hot path
- **Primary focus:** 99th percentile and max jitter, not only median
- **Requirement:** reproducible benchmark methodology checked into repo

#### Exit criteria

- repeated benchmark runs within tolerable spread
- sub-10 ms coordination demonstrated on baseline path
- benchmark artifacts versioned

#### Rollback rule

Do not proceed to `scx_gaia` if:
- tail latency remains unstable
- results are irreproducible
- root causes are not separated between kernel, IRQ, and userspace effects

### Phase 0D — GUARDIAN enforcement layer

#### Objective

Stand up GUARDIAN as a **stackable, narrow-scope enforcement layer**, not as a replacement for SELinux/AppArmor.

#### Implementation posture

- minimal LSM module and/or BPF-LSM prototype
- audit + deny on narrowly scoped actions first
- explicit policy surface for:
  - disallowed actuation
  - unsafe file/network/device actions
  - checkpoint integrity protection
  - critical memory/audit paths

#### Exit criteria

- narrow deny rules work predictably
- audit events are visible and attributable
- policy failures fail closed on critical paths
- GUARDIAN rules do not destabilize the host

#### Rollback rule

Rollback to audit-only mode if:
- false positives block baseline bringup
- policy ordering conflicts break core services
- enforcement causes instability that cannot be traced rapidly

### Phase 0E — `scx_gaia` BPF scheduler

#### Objective

Layer GAIA-specific dispatch policy on top of a proven RT substrate.

#### Design target

Implement classed queues such as:
- `DSQ_GUARDIAN_STOP`
- `DSQ_NEXUS_CRITICAL`
- `DSQ_DOMAIN_RT`
- `DSQ_INTERACTIVE`
- `DSQ_BACKGROUND`

#### Critical rule

Treat `scx_gaia` as **kernel-version-coupled code**. Pin it to the selected kernel line.

#### Exit criteria

- scheduler loads and unloads cleanly
- class mapping is documented
- latency under `scx_gaia` is equal to or better than baseline for critical paths
- noncritical work is de-prioritized without starving required services

#### Rollback rule

Immediately rollback to the proven baseline scheduler if:
- tail latency worsens
- task starvation appears
- kernel upgrades break the scheduler surface
- benchmarking becomes less reproducible

---

## Phase 1 — IPC Transport Layer (GAIA-Core)

### Why this phase unblocks everything else

IPC is the nervous system. Memory, validators, and neuromorphic execution all depend on typed transport and causal ordering.

### Phase 1A — L1 hot path

#### Build

- `memfd` shared-memory rings
- `eventfd` / `futex` signaling
- zero-copy local transport for critical paths

#### Exit criteria

- single-host hot path proven
- message handoff latency benchmarked
- clear ownership / lifetime model documented

### Phase 1B — L2 async plane

#### Build

- `io_uring` for socket I/O, WAL, audit log I/O, and background persistence

#### Exit criteria

- submission/completion path benchmarked
- WAL and audit writes are bounded and observable
- backpressure behavior documented

### Phase 1C — L3 typed service layer

#### Build

- gRPC + Protobuf schemas for:
  - `NexusSyncService`
  - `GuardianPolicyService`
  - `MemoryRetrievalService`
  - `CheckpointService`
  - `ValidationService`

#### Exit criteria

- schemas versioned
- request/response and error contracts explicit
- contract tests present

### Phase 1D — L4 causal ordering

#### Build

- vector clocks for **state-mutating** cross-core messages
- causal envelopes attached only where needed

#### Exit criteria

- causal replay can reconstruct mutation order
- out-of-order delivery is detectable
- read-only/ephemeral paths remain lightweight

#### Rollback rule

If L4 overhead materially harms throughput or latency, keep causal envelopes only on state-mutating messages and avoid promoting them to every transport path.

---

## Phase 2 — Holographic Memory Foundation (GAIA-Core)

### Governing principle

**The canonical memory log is truth. Indexes are rebuildable acceleration layers.**

### Phase 2A — Canonical log and `MemoryAtom`

#### Build

- `MemoryAtom` data model
- canonical append log
- immutable event identity
- provenance, timestamping, dependency fields

#### Exit criteria

- replayable append-only log
- schema versioning present
- index rebuild from log is possible

### Phase 2B — Hot tier

#### Build

- FAISS HNSW hot tier
- session-token read-your-writes semantics
- query filters for freshness, scope, and visibility

#### Exit criteria

- sub-100 ms recall target for hot working set
- session-scoped read-your-writes verified
- recall quality and latency benchmarked together

### Phase 2C — Causal envelope

#### Build

- Hybrid Logical Clock timestamps
- dependency sets
- visibility and causality metadata on mutable memory events

#### Exit criteria

- causal visibility filters work
- conflicting updates are detectable
- replay engine preserves partial order

### Phase 2D — Capacity tier

#### Build

- DiskANN-backed SSD capacity tier
- regional or domain sharding strategy

#### Exit criteria

- tiered retrieval path works
- rebuild procedure is documented
- cold-tier latency and recall thresholds defined

### Phase 2E — Federation and rebuild

#### Build

- federated search router
- index rebuild from canonical log
- visibility filters across shards / devices

#### Exit criteria

- federated search is deterministic under documented visibility rules
- rebuild drills succeed
- loss of an index does not destroy truth state

#### Rollback rule

If hot-tier indexing or capacity-tier behavior diverges from the canonical log, the log remains source of truth and indexes must be rebuilt rather than hand-repaired.

---

## Phase 3 — Neuromorphic Cores (GAIA-Core + GAIA-IoT)

### Governing principle

Do **not** start with all four environmental cores. Pilot on **AERO first**.

### Why AERO first

AERO best matches the early neuromorphic execution profile:
- sparse signals
- threshold-oriented event handling
- edge-friendly deployment
- lower first-pilot semantic burden than VITA

### Phase 3A — Package skeleton

#### Build

- `GAIA-Core/neuromorphic/`
- `DomainCoreExecutor` interface
- standard modes:
  - `run_reference`
  - `run_lava_cpu`
  - `run_loihi2`
  - `run_classical`

### Phase 3B — AERO Brian2 reference

#### Build

- Brian2 reference prototype for AERO
- deterministic test dataset
- baseline metrics

#### Exit criteria

- reference model runs reproducibly
- metrics and equations versioned
- benchmark dataset fixed

### Phase 3C — Lava CPU port + parity

#### Build

- Lava CPU implementation of AERO
- Brian2↔Lava parity tests

#### Exit criteria

- parity thresholds documented
- CPU backend stable
- failure cases logged

### Phase 3D — Classical fallbacks

#### Build

- classical fallback backends for TERRA, AQUA, AERO, VITA

#### Exit criteria

- same I/O contract across execution modes
- fallback reasons explicit
- parity or bounded drift documented

### Phase 3E — GAIA-IoT adapters

#### Build

- physical sensor adapters
- stream ingestion bridge
- bounded edge execution path

#### Rollback rule

Do not promote Loihi-targeted work to critical path if public tooling, hardware access, or parity limits block reproducibility. Keep Brian2 reference + Lava CPU + classical fallback as the operational default.

---

## Phase 4 — Energy Optimization and Distribution Repos

### Why this phase comes last

Energy and carbon-aware behavior should sit on top of a proven substrate, not compensate for an unproven one.

### Phase 4A — Power modes

#### Build

- `power_mode_controller.py`
- six consciousness-aware modes

Suggested modes:
- Sentinel
- Balanced
- Intensive
- Recovery
- Steady-State
- Emergency/Conservation

#### Exit criteria

- mode transitions are explicit
- transitions are logged
- critical paths are protected from inappropriate throttling

### Phase 4B — Carbon-aware elastic scheduling

#### Build

- `carbon_scheduler.py`
- shift only Tier 3 elastic work

#### Exit criteria

- hard real-time paths never depend on carbon shifting
- policy is explainable and auditable
- workloads are tagged by elasticity tier

### Phase 4C — Repo propagation

#### Target repos

- `GAIA-Core`
- `GAIA-Desktop`
- `GAIA-Laptop`
- `GAIA-IoT`
- `GAIA-Server`
- `GAIA-Meta`

#### Requirement

All distribution repos inherit the GAIA-Core substrate rather than reinterpreting it independently.

#### Exit criteria

- substrate interfaces match across repos
- power mode propagation documented
- cross-repo consistency pass complete

---

## Kernel Config Checklist

This checklist is the minimum canonical baseline for bringup and review.

### Real-time and scheduling

- `CONFIG_PREEMPT_RT`
- `CONFIG_BPF`
- `CONFIG_BPF_SYSCALL`
- `CONFIG_SCHED_CLASS_EXT` or equivalent kernel support for `sched_ext` on chosen line
- `CONFIG_CGROUPS`
- `CONFIG_CGROUP_CPUACCT`
- `CONFIG_CGROUP_SCHED`
- `CONFIG_CPUSETS`

### Security / GUARDIAN

- LSM stacking support for chosen kernel / distro posture
- BPF LSM support if using BPF-LSM prototype path
- audit support enabled

### Measurement and traceability

- tracing / perf / ftrace or equivalent measurement tooling enabled
- BTF and BPF build requirements satisfied for `sched_ext` work

### Topology and CPU management

- cpuset enabled
- IRQ affinity management available
- deterministic boot params documented if used

### Review note

`CONFIG_RT_GROUP_SCHED` requires special review because of the cgroup v2 RT caveat. If enabled, plan around the documented root-cgroup requirement for RT processes. If disabled, document the tradeoff explicitly.

---

## Benchmark Thresholds

These are initial engineering targets, not final scientific claims.

### Kernel / scheduler

- sub-10 ms NEXUS↔GUARDIAN coordination hot path
- stable 99th percentile behavior under representative background load
- scheduler regression budget defined before introducing `scx_gaia`

### IPC

- zero-copy local hot path benchmarked independently of network RPC
- causal envelope overhead measured separately from transport overhead
- audit log write path bounded and observable

### Memory

- hot-tier retrieval target: sub-100 ms on defined working set
- replay correctness takes precedence over index speed
- rebuild-from-log drills succeed

### Neuromorphic

- reference vs Lava parity thresholds documented
- fallback path always available
- pilot execution limited to AERO until parity discipline is proven

### Energy

- no power mode allowed to break kernel timing contracts
- no carbon-aware scheduling on hard real-time or critical integrity paths

---

## Repo Placement

```text
GAIA-Core/
  docs/
    00-index/
    02-architecture/
      gaia-core-critical-path_v1.0.md
  kernel/
    configs/
    patches/
    benchmarks/
    guardian-lsm/
    sched_ext/
  ipc/
    proto/
    local/
    async/
  memory/
    canonical-log/
    hot-tier/
    capacity-tier/
  neuromorphic/
  energy/
  tests/
```

---

## Phase Gates Summary

| Phase | Gate to enter | Gate to exit |
|---|---|---|
| P0 | target hardware selected | sub-10 ms coordination baseline + stable measurements |
| P1 | kernel substrate stable | typed IPC + causal mutation ordering validated |
| P2 | IPC schemas defined | canonical log + hot tier + rebuild discipline proven |
| P3 | memory + IPC stable | AERO Brian2/Lava parity + fallback contract operational |
| P4 | substrate proven | power/carbon policies propagated without violating core contracts |

---

## Mandatory Non-Goals During Bringup

Do not let these derail the critical path:

- full multi-agent federation before IPC and memory are stable
- full Loihi production dependency before Lava CPU parity is proven
- all environmental cores live at once
- energy optimization before timing contracts are established
- custom scheduler work before PREEMPT_RT baseline is measured
- broad GUARDIAN policy before narrow-scope audit/deny rules are stable

---

## Failure Conditions

Pause or rollback if any of the following occur:

- kernel timing improves in average terms but tail latency degrades materially
- `scx_gaia` becomes the only way the system appears to meet targets
- GUARDIAN policy becomes too broad to debug safely
- memory index behavior diverges from canonical log truth
- neuromorphic pilot becomes blocked by nonreproducible hardware/tooling dependencies
- energy policy changes timing behavior on critical paths

---

## Immediate Next Build Sequence

1. Commit this document into `GAIA-Core/docs/02-architecture/`
2. Add kernel config baseline and measurement harness placeholders
3. Create `kernel/guardian-lsm/` and `kernel/sched_ext/` starter directories
4. Stand up benchmark scripts and artifact capture
5. Freeze Phase 0 exit criteria before writing `scx_gaia`
6. Only after Phase 0 proof, begin IPC transport implementation

---

## Canonical Law for This Document

> **No higher-layer contract in GAIA is considered real until the kernel, transport, and memory substrate can enforce and measure it.**

And more sharply:

> **Timing first. Transport second. Memory third. Meaning later.**

---

## Reference Grounding

This critical path is grounded in current upstream or official documentation for:

- Linux longterm release posture
- PREEMPT_RT behavior
- cgroup v2 realtime caveat
- `sched_ext` ABI instability
- LSM stacking / BPF userspace APIs
- `io_uring` async I/O model
- gRPC service model
- FAISS HNSW indexing
- Lava / Brian2 / Brian2Lava execution realities

These references should be mirrored into the GAIA research registry or source appendix if this document is promoted to canonical status.
