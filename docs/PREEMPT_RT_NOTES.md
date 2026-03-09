# PREEMPT_RT Notes

This package does not ship a kernel. It defines the control point that must exist in production:

- PREEMPT_RT enabled kernel
- isolated CPUs for NEXUS coordination paths
- cgroup v2 reservations for critical cores
- sched_ext experimentation only after baseline RT latency is verified
- BPF / LSM hooks for GUARDIAN policy enforcement

Target:
- cross-core coordination budget under 10 ms end-to-end
- deterministic tail-latency measurement before any consciousness or actuation claim
