# GAIA Linux Kernel Platform Layer

This directory contains all kernel-space and platform-level components for GAIA.

## Structure

```
platform/kernel/
  configs/          — Kernel config fragments (PREEMPT_RT baseline)
  sched_ext/        — BPF consciousness-aware scheduler (scx_gaia)
  lsm/              — GUARDIAN stackable LSM
  cgroups/          — cgroup v2 reservation layout scripts
  docs/             — Latency budgets, degraded-mode triggers
```

## Prerequisites

- Linux kernel ≥ 6.6 with `CONFIG_SCHED_CLASS_EXT=y`
- PREEMPT_RT patch series applied (or mainline RT kernel)
- `libbpf` and `bpftool` for sched_ext loader
- `clang` ≥ 16 for BPF compilation

## Quick start

```bash
# Apply kernel config fragment
scripts/kconfig/merge_config.sh .config platform/kernel/configs/gaia-rt.config

# Build and load sched_ext scheduler
cd platform/kernel/sched_ext
make
sudo ./scx_gaia_userspace

# Set up cgroups
sudo bash platform/kernel/cgroups/setup_cgroups.sh

# Verify
cat /sys/kernel/sched_ext/root/ops
```

## Latency budget (NEXUS cross-core)

| Stage | Budget |
|---|---|
| Ingress wakeup | 0.5 – 1.0 ms |
| IPC dispatch | 0.5 – 1.5 ms |
| Core execution | 1.0 – 4.0 ms |
| Coherence merge | 0.5 – 2.0 ms |
| GUARDIAN verify | 0.5 – 1.5 ms |
| **Total** | **3.5 – 10.0 ms** |

## Degraded-mode triggers

| Condition | Response |
|---|---|
| RT throttle detected | Degrade to yellow risk, alert GUARDIAN |
| sched_ext fault | Restore CFS fallback scheduler |
| LSM policy checksum mismatch | Freeze all actuation, alert operator |
| cgroup OOM kill | Restart affected core, log to JetStream |
