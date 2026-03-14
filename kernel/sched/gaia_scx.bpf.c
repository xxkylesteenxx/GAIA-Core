// SPDX-License-Identifier: GPL-2.0
/*
 * gaia_scx.bpf.c
 *
 * Version-pinned sched_ext prototype for designated GAIA workloads.
 * This file is designed as a starting point for Linux kernels with sched_ext
 * enabled. It intentionally uses a conservative partial-switch model.
 *
 * Build assumptions:
 * - kernel built with CONFIG_SCHED_CLASS_EXT=y
 * - vmlinux.h generated from the target kernel
 * - include paths adjusted for the local kernel tree or sched_ext headers
 */

#include "vmlinux.h"
#include <bpf/bpf_core_read.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

/*
 * NOTE:
 * Depending on your kernel / include layout, you may need to adjust this include.
 * In many sched_ext setups, a helper header from tools/sched_ext is used here.
 */
#include "scx/common.bpf.h"

char LICENSE[] SEC("license") = "GPL";

#define GAIA_WL_BACKGROUND        0
#define GAIA_WL_INTERACTIVE       1
#define GAIA_WL_CRITICAL_SERVICE  2
#define GAIA_WL_POLICY_ENGINE     3
#define GAIA_WL_SAFETY_MONITOR    4

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 4096);
    __type(key,   u32);   /* pid */
    __type(value, u32);   /* workload class */
} pid_class SEC(".maps");

static __always_inline u64 gaia_slice_for_class(u32 class_id)
{
    switch (class_id) {
    case GAIA_WL_SAFETY_MONITOR:    return SCX_SLICE_DFL * 4;
    case GAIA_WL_POLICY_ENGINE:     return SCX_SLICE_DFL * 3;
    case GAIA_WL_CRITICAL_SERVICE:  return SCX_SLICE_DFL * 2;
    case GAIA_WL_INTERACTIVE:       return SCX_SLICE_DFL;
    case GAIA_WL_BACKGROUND:
    default:                        return SCX_SLICE_DFL / 2;
    }
}

s32 BPF_STRUCT_OPS(gaia_select_cpu, struct task_struct *p, s32 prev_cpu, u64 wake_flags)
{
    s32  cpu;
    bool direct = false;

    cpu = scx_bpf_select_cpu_dfl(p, prev_cpu, wake_flags, &direct);
    if (direct)
        scx_bpf_dsq_insert(p, SCX_DSQ_LOCAL, SCX_SLICE_DFL, 0);

    return cpu;
}

void BPF_STRUCT_OPS(gaia_enqueue, struct task_struct *p, u64 enq_flags)
{
    u32  pid      = BPF_CORE_READ(p, pid);
    u32 *class_id = bpf_map_lookup_elem(&pid_class, &pid);
    u64  slice    = SCX_SLICE_DFL;

    if (class_id)
        slice = gaia_slice_for_class(*class_id);

    scx_bpf_dsq_insert(p, SCX_DSQ_GLOBAL, slice, enq_flags);
}

s32 BPF_STRUCT_OPS_SLEEPABLE(gaia_init)
{
    return 0;
}

void BPF_STRUCT_OPS(gaia_exit, struct scx_exit_info *ei)
{
    /* Placeholder for telemetry or ring-buffer event publication. */
    (void)ei;
}

SEC(".struct_ops")
struct sched_ext_ops gaia_ops = {
    .select_cpu = (void *)gaia_select_cpu,
    .enqueue    = (void *)gaia_enqueue,
    .init       = (void *)gaia_init,
    .exit       = (void *)gaia_exit,
    .flags      = SCX_OPS_SWITCH_PARTIAL,
    .name       = "gaia_scx",
};
