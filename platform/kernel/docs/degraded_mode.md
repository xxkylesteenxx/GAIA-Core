# GAIA Degraded Mode Specification

GAIA must degrade gracefully rather than fail catastrophically.
Each degraded-mode trigger has a defined detection method,
automatic response, and recovery path.

## Degraded mode levels

| Level | Name | Description |
|---|---|---|
| 0 | Normal | All subsystems nominal |
| 1 | Cautious | One non-critical subsystem degraded; monitoring elevated |
| 2 | Restricted | Critical path degraded; actuation limited to GREEN-class only |
| 3 | Safe-hold | All actuation frozen; human operator required to resume |
| 4 | Emergency | Hardware fault or LSM policy violation; hard shutdown of affected cores |

## Automatic degraded-mode transitions

### RT throttle detected
- **Detection:** `rt_throttle_count` in `/proc/sched_debug` increments
- **Auto response:** Signal GUARDIAN via IPC `DataClass.A` envelope; set risk level YELLOW
- **Recovery:** RT throttle clears for 30 s → auto-restore to NORMAL
- **Escalation:** RT throttle persists > 5 min → degrade to RESTRICTED

### sched_ext fault
- **Detection:** `scx_gaia_userspace` exits with non-zero code or `scx_exit_info.reason != 0`
- **Auto response:** Immediately restore CFS (`sched_setscheduler(SCHED_OTHER)`) for all GAIA tasks
- **Recovery:** Manual: `sudo ./scx_gaia_userspace` after verifying BPF CO-RE compatibility
- **Escalation:** 3 faults in 10 min → disable sched_ext permanently until next reboot

### LSM policy checksum mismatch
- **Detection:** `guardian_lsm` kernel log contains `POLICY CHECKSUM MISMATCH`
- **Auto response:** `actuation_frozen = true` in kernel; all actuation writes blocked at LSM level
- **Recovery:** Operator must: (1) verify policy file integrity, (2) run `policy_loader` with correct manifest, (3) explicitly unfreeze via sysfs
- **Escalation:** No automatic unfreeze — always requires human operator sign-off

### cgroup OOM kill
- **Detection:** `memory.events` `oom_kill` counter increments for a GAIA cgroup
- **Auto response:** GAIA watchdog restarts the affected core process; publishes `CORE_OOM_RESTART` event to `GAIA.GUARDIAN` JetStream stream
- **Recovery:** Automatic if memory pressure resolves; otherwise increase `memory.max` for that core
- **Escalation:** 3 OOM kills in 5 min for same core → degrade that core to RESTRICTED
