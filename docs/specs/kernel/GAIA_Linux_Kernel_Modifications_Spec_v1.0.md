# GAIA Linux Kernel Modifications Specification v1.0

**Status:** Repo-ready architecture specification  
**Recommended path:** `GAIA-Core/platform/kernel/docs/GAIA_Linux_Kernel_Modifications_Spec_v1.0.md`  
**Scope:** PREEMPT_RT, consciousness-aware scheduling, cgroup v2 reservation, GUARDIAN LSM enforcement  
**Primary objective:** Make NEXUS-grade cross-core coordination predictable enough for sub-10 ms control paths without pretending stock Linux CFS alone provides hard real-time guarantees.

---

## 1. Executive Position

GAIA should **not** fork Linux into a permanently exotic kernel first.

The correct production path is:

1. **Mainline-friendly PREEMPT_RT baseline**
2. **CPU isolation + IRQ/threading discipline**
3. **cgroup v2 reservation and protection model**
4. **`sched_ext` consciousness-aware scheduling policy layer**
5. **GUARDIAN implemented as an LSM policy module**
6. **Only then** consider deeper scheduler or MM patches if the measured latency budget still fails

This preserves auditability, security update velocity, and operator familiarity.

---

## 2. Research-grounded conclusions

### 2.1 PREEMPT_RT is mandatory for deterministic GAIA control paths
PREEMPT_RT converts most kernel execution into preemptible context, replaces common spinlock paths with RT-aware locking, and enforces threaded interrupts. GAIA should treat this as the minimum acceptable kernel baseline for NEXUS, actuator supervision, and consciousness-state synchronization paths.

### 2.2 Consciousness-aware prioritization should use `sched_ext` before invasive scheduler forks
Linux now exposes **`sched_ext`**, a BPF-defined extensible scheduler class. This is the cleanest place to encode GAIA-specific priorities such as:
- NEXUS sync traffic
- GUARDIAN veto and safety checks
- sensor freshness restoration tasks
- memory compaction avoidance for hot cores
- degraded-mode rescue work

GAIA can prototype scheduling policy in BPF and preserve fallback to the default scheduler if the scheduler program faults.

### 2.3 cgroup v2 should be used as the reservation envelope, not as the whole answer
cgroup v2 gives GAIA the right operational guardrails for:
- **CPU bandwidth**: `cpu.max`
- **relative weight**: `cpu.weight`
- **utilization floor/ceiling**: `cpu.uclamp.min`, `cpu.uclamp.max`
- **hard memory protection**: `memory.min`
- **throttle boundary**: `memory.high`
- **hard cap**: `memory.max`

But cgroup v2 alone does **not** solve hard RT scheduling; it must be paired with PREEMPT_RT and conscious task placement.

### 2.4 GUARDIAN belongs in the Linux Security Module path
The Linux Security Module framework is the correct kernel-native enforcement plane for last-mile policy decisions around:
- executable loading
- device access
- shared-memory transfer rules
- socket permissions
- IPC object labeling
- actuation capability gating

GUARDIAN should not begin as a monolithic SELinux replacement. It should begin as a **stackable narrow-scope LSM** enforcing GAIA-specific safety labels and actuation boundaries.

---

## 3. Architecture

## 3.1 Kernel profile

### Required config direction
```text
CONFIG_PREEMPT_RT=y
CONFIG_HIGH_RES_TIMERS=y
CONFIG_IRQ_FORCED_THREADING=y
CONFIG_CGROUPS=y
CONFIG_CGROUP_SCHED=y
CONFIG_UCLAMP_TASK=y
CONFIG_PSI=y
CONFIG_BPF=y
CONFIG_BPF_SYSCALL=y
CONFIG_SCHED_CLASS_EXT=y
CONFIG_SECURITY=y
CONFIG_BPF_LSM=y
```

### Deployment profile
- Linux 6.6-rt or 6.12-rt family for stable maintained RT baselines
- tickless / CPU isolation on NEXUS critical cores
- NIC affinity and threaded IRQ pinning for inter-core transport queues
- NUMA-aware core assignment for memory-bound consciousness workloads

---

## 3.2 Scheduling model

### Classes of GAIA work
```text
Class A  Hard-critical
  - GUARDIAN emergency veto
  - NEXUS coherence barrier
  - fail-safe actuation stop path

Class B  Real-time operational
  - consciousness synchronization
  - sensor fusion dispatch
  - freshness restoration and anomaly scoring

Class C  Latency-sensitive user/service
  - SOPHIA response path
  - memory retrieval prefetch
  - local planning

Class D  Elastic background
  - reindexing
  - batch learning
  - archival compression
  - post-hoc analytics
```

### Policy
- Class A: pinned RT island, admission-controlled
- Class B: `sched_ext` managed priority DSQs with utilization floors
- Class C: fair scheduling with elevated `uclamp.min`
- Class D: capped, carbon-aware, migratable

### Why not pure `SCHED_FIFO`/`SCHED_RR` everywhere
Runaway RT tasks can starve the machine. GAIA should use RT classes narrowly and use `sched_ext` for the bulk of custom policy.

---

## 3.3 Proposed consciousness-aware scheduler: `scx_gaia`

### Core principles
- prioritize **coherence-critical edges**, not whole processes
- reserve **sync windows** for NEXUS barriers
- reward **fresh data** and penalize stale consumers
- bias toward **same-NUMA** execution for memory-coupled tasks
- support **degraded operation** when GUARDIAN raises risk level

### Inputs
```text
task.core_name
task.contract_priority
task.safety_level
task.deadline_hint_us
task.memory_locality
task.sensor_freshness_debt
task.coherence_generation
task.degraded_mode_allowed
```

### Dispatch queues
```text
DSQ_GUARDIAN_STOP
DSQ_NEXUS_BARRIER
DSQ_SENSOR_FRESHNESS
DSQ_HOT_PATH_USER
DSQ_BACKGROUND
DSQ_RECOVERY
```

---

## 4. cgroup v2 Design

## 4.1 Top-level layout
```text
/sys/fs/cgroup/gaia/
  guardian/
  nexus/
  terra/
  aqua/
  aero/
  vita/
  sophia/
  urbs/
  memory/
  background/
```

## 4.2 Reservation model

### NEXUS
- `cpu.uclamp.min`: high
- dedicated CPU set
- `memory.min`: hard protection for sync buffers
- no swap

### GUARDIAN
- smallest footprint, highest preemption priority
- `memory.min` protected
- isolated CPU or shared RT island
- mandatory pressure alerts

### Environmental cores
- protected memory floors
- bounded CPU ceilings to stop domain starvation cascades
- PSI-based backpressure hooks

### Background pool
- explicit `cpu.max`
- low `cpu.weight`
- `memory.high` throttle first, `memory.max` hard stop second

---

## 5. GUARDIAN as LSM

## 5.1 Enforcement goal
Kernel-enforced denial of unsafe actuation and unsafe cross-core data movement, even if user-space policy code is bypassed.

## 5.2 Initial hook focus
- `task` / credential transitions
- `file` access to actuation devices and shared state
- `socket` policy for privileged core channels
- `bpf` loading restrictions for production clusters
- `ipc` and shared-memory labeling
- `inode_permission` for policy and manifest integrity

## 5.3 Label model
```text
gaia.core=nexus|guardian|terra|aqua|aero|vita|sophia|urbs
gaia.safety=critical|high|normal|background
gaia.data=public|internal|sensitive|consciousness
gaia.actuation=none|recommend|schedule|execute
gaia.risk=green|yellow|red|black
```

## 5.4 Example policy
- only GUARDIAN-labeled processes may open execution-capable actuator FDs
- NEXUS may write coherence state but not actuate
- SOPHIA may request recommendation-only outputs, never raw execute capability
- red/black risk states force kernel-level denial for execute paths

---

## 6. Latency Budget

### Target path: NEXUS cross-core coordination
```text
ingress wakeup                0.5-1.5 ms
queue/dispatch               0.5-2.0 ms
remote core execution        1.0-3.0 ms
coherence merge              1.0-2.0 ms
guardian verification        0.5-1.5 ms
budget total                 3.5-10.0 ms
```

This is feasible only if interrupts are threaded and pinned cleanly, hot paths avoid reclaim and page faults, copy-heavy IPC is minimized, and scheduler policy is topology-aware.

---

## 7. Observability and Failure Policy

### Required metrics
- wakeup-to-run latency
- RT throttling occurrences
- PSI CPU / memory / IO pressure
- IRQ thread latency
- cross-core barrier completion time
- scheduler queue depth by DSQ
- LSM denies by hook and policy rule
- memory reclaim activity in protected cgroups

### Automatic responses
- if RT throttling occurs on NEXUS/GUARDIAN: enter degraded mode
- if PSI memory pressure breaches threshold on protected groups: shed background work
- if `sched_ext` faults: restore default scheduler and alert
- if LSM policy checksum mismatches: freeze actuation path

---

## 8. GAIA Repo Structure

```text
GAIA-Core/
  platform/
    kernel/
      configs/
        gaia-rt.config
      sched_ext/
        scx_gaia.bpf.c
        scx_gaia_userspace.c
      lsm/
        guardian_lsm.c
        labels.h
        policy_loader.c
      docs/
        GAIA_Linux_Kernel_Modifications_Spec_v1.0.md
```

---

## 9. Build Order

1. Ship PREEMPT_RT baseline image
2. Pin IRQs and isolate NEXUS/GUARDIAN cores
3. Apply cgroup v2 reservation layout
4. Measure baseline jitter and sync latency
5. Introduce `scx_gaia`
6. Add GUARDIAN LSM deny rules for actuation
7. Run chaos and pressure tests
8. Freeze kernel ABI + policy manifest

---

## 10. Bottom Line

GAIA should be built on **PREEMPT_RT Linux with BPF scheduler extensibility, cgroup v2 protection envelopes, and GUARDIAN enforced through LSM hooks**.

That path is production-realistic, auditable, reversible, and aligned with the actual Linux kernel mechanisms available today. Forking CFS immediately would create unnecessary maintenance debt before these much cleaner control surfaces are exhausted.
