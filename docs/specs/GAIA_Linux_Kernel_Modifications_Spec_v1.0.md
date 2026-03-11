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

But cgroup v2 alone does **not** solve hard RT scheduling, especially for all RT workloads; it must be paired with PREEMPT_RT and conscious task placement.

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

### 3.1 Kernel profile

#### Required config direction
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

#### Deployment profile
- Linux 6.6-rt or 6.12-rt family for stable maintained RT baselines
- tickless / CPU isolation on NEXUS critical cores
- NIC affinity and threaded IRQ pinning for inter-core transport queues
- NUMA-aware core assignment for memory-bound consciousness workloads

---

### 3.2 Scheduling model

#### Classes of GAIA work
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

#### Policy
- Class A: pinned RT island, admission-controlled
- Class B: `sched_ext` managed priority DSQs with utilization floors
- Class C: fair scheduling with elevated `uclamp.min`
- Class D: capped, carbon-aware, migratable

---

## 4. cgroup v2 design

### 4.1 Top-level layout
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

---

## 5. GUARDIAN as LSM

### 5.1 Label model
```text
gaia.core=nexus|guardian|terra|aqua|aero|vita|sophia|urbs
gaia.safety=critical|high|normal|background
gaia.data=public|internal|sensitive|consciousness
gaia.actuation=none|recommend|schedule|execute
gaia.risk=green|yellow|red|black
```

---

## 6. Bottom line

GAIA should be built on **PREEMPT_RT Linux with BPF scheduler extensibility, cgroup v2 protection envelopes, and GUARDIAN enforced through LSM hooks**.
