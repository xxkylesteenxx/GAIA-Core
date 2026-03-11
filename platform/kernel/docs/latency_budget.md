# GAIA NEXUS Cross-Core Latency Budget

**Target total: 3.5 – 10.0 ms** for a full NEXUS coherence cycle:
ingress wakeup → IPC dispatch → core execution → coherence merge → GUARDIAN verification.

## Stage breakdown

| Stage | Technology | Min ms | Max ms | Notes |
|---|---|---|---|---|
| Ingress wakeup | PREEMPT_RT + sched_ext DSQ_NEXUS_BARRIER | 0.5 | 1.0 | RT island, isolated cores |
| IPC dispatch | memfd ring (same-host) or gRPC (cross-host) | 0.5 | 1.5 | Class A envelope required |
| Core execution | NEXUS consciousness tick | 1.0 | 4.0 | Includes inference budget |
| Coherence merge | VectorClock merge + causal broadcast | 0.5 | 2.0 | Causal holdback adds latency |
| GUARDIAN verify | Policy check + LSM label validation | 0.5 | 1.5 | Hard veto path is synchronous |
| **Total** | | **3.5** | **10.0** | |

## Measurement

```bash
# wakeup-to-run latency via ftrace
echo 1 > /sys/kernel/tracing/events/sched/sched_wakeup/enable
echo 1 > /sys/kernel/tracing/events/sched/sched_switch/enable
cat /sys/kernel/tracing/trace_pipe

# RT throttle events
grep rt_throttle /proc/sched_debug

# sched_ext stats
cat /sys/kernel/sched_ext/root/stats

# PSI pressure per cgroup
cat /sys/fs/cgroup/gaia/nexus/cpu.pressure
cat /sys/fs/cgroup/gaia/nexus/memory.pressure
```

## Degraded-mode triggers

| Trigger | Detection | Response |
|---|---|---|
| RT throttle | `/proc/sched_debug` rt_throttle_count increase | Degrade to YELLOW, alert GUARDIAN via IPC |
| sched_ext fault | `scx_gaia_userspace` exit with error | Restore CFS (`SCHED_OTHER`), re-pin when safe |
| LSM policy checksum mismatch | `guardian_lsm` kernel log `POLICY CHECKSUM MISMATCH` | Freeze all actuation, alert operator |
| cgroup OOM kill | `memory.events` oom_kill > 0 | Restart affected core, publish to `GAIA.GUARDIAN` JetStream |
| Causal holdback depth > 100 | `IpcObservability.snapshot()` | Warn, check network partition |
| NEXUS coherence latency > 10 ms | ftrace `sched_wakeup` delta | Warn, reduce consciousness tick rate |
