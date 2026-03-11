// SPDX-License-Identifier: GPL-2.0
// scx_gaia — GAIA consciousness-aware BPF scheduler
//
// Implements sched_ext DSQs mapped to GAIA work classes:
//   DSQ_GUARDIAN_STOP    — Class A: GUARDIAN veto / emergency stop (RT island)
//   DSQ_NEXUS_BARRIER    — Class A: NEXUS coherence barrier (RT island)
//   DSQ_SENSOR_FRESHNESS — Class B: sensor ingestion freshness deadline
//   DSQ_HOT_PATH_USER    — Class C: SOPHIA response, memory prefetch
//   DSQ_BACKGROUND       — Class D: reindexing, batch learning
//   DSQ_RECOVERY         — Recovery/watchdog tasks
//
// Latency budget: NEXUS cross-core total 3.5-10.0 ms

#include <scx/common.bpf.h>

// DSQ identifiers
#define DSQ_GUARDIAN_STOP    0ULL
#define DSQ_NEXUS_BARRIER    1ULL
#define DSQ_SENSOR_FRESHNESS 2ULL
#define DSQ_HOT_PATH_USER    3ULL
#define DSQ_BACKGROUND       4ULL
#define DSQ_RECOVERY         5ULL

// Per-task storage: GAIA work class label
struct task_ctx {
    u32 work_class;   // 0=A_critical, 1=A_RT, 2=C_latency, 3=D_background
    u64 enqueue_ns;
    u64 last_dsq;
};

struct {
    __uint(type, BPF_MAP_TYPE_TASK_STORAGE);
    __uint(map_flags, BPF_F_NO_PREALLOC);
    __type(key, int);
    __type(value, struct task_ctx);
} task_ctx_map SEC(".maps");

// Observability counters
struct {
    __uint(type, BPF_MAP_TYPE_ARRAY);
    __uint(max_entries, 6);
    __type(key, u32);
    __type(value, u64);
} dsq_enqueue_counts SEC(".maps");

static __always_inline u64 task_to_dsq(struct task_struct *p)
{
    struct task_ctx *tctx = bpf_task_storage_get(
        &task_ctx_map, p, NULL, BPF_LOCAL_STORAGE_GET_F_CREATE);
    if (!tctx)
        return DSQ_HOT_PATH_USER;  // safe default

    // Map sched_priority and GAIA work class label to DSQ
    int prio = p->prio;  // lower = higher priority in Linux
    if (prio <= 50)      // RT priorities [0-99] are negative in nice scale
        return DSQ_GUARDIAN_STOP;
    if (prio <= 60)
        return DSQ_NEXUS_BARRIER;
    if (tctx->work_class == 1)
        return DSQ_SENSOR_FRESHNESS;
    if (tctx->work_class == 3)
        return DSQ_BACKGROUND;
    return DSQ_HOT_PATH_USER;
}

s32 BPF_STRUCT_OPS(scx_gaia_init_task, struct task_struct *p,
                   struct scx_init_task_args *args)
{
    struct task_ctx *tctx = bpf_task_storage_get(
        &task_ctx_map, p, NULL, BPF_LOCAL_STORAGE_GET_F_CREATE);
    if (!tctx)
        return -ENOMEM;
    tctx->work_class = 2;  // default: latency-sensitive
    tctx->enqueue_ns = 0;
    tctx->last_dsq = DSQ_HOT_PATH_USER;
    return 0;
}

void BPF_STRUCT_OPS(scx_gaia_enqueue, struct task_struct *p, u64 enq_flags)
{
    u64 dsq_id = task_to_dsq(p);
    u32 dsq_key = (u32)dsq_id;
    u64 *cnt = bpf_map_lookup_elem(&dsq_enqueue_counts, &dsq_key);
    if (cnt)
        __sync_fetch_and_add(cnt, 1);

    // Class A tasks: zero slice (preempt immediately when dispatched)
    if (dsq_id == DSQ_GUARDIAN_STOP || dsq_id == DSQ_NEXUS_BARRIER) {
        scx_bpf_dispatch(p, dsq_id, 0, enq_flags);
        return;
    }
    // All other classes: 4 ms nominal slice
    scx_bpf_dispatch(p, dsq_id, 4000000ULL, enq_flags);
}

void BPF_STRUCT_OPS(scx_gaia_dispatch, s32 cpu, struct task_struct *prev)
{
    // Strict priority order: GUARDIAN_STOP > NEXUS_BARRIER > SENSOR > HOT > RECOVERY > BACKGROUND
    if (scx_bpf_consume(DSQ_GUARDIAN_STOP))    return;
    if (scx_bpf_consume(DSQ_NEXUS_BARRIER))    return;
    if (scx_bpf_consume(DSQ_SENSOR_FRESHNESS)) return;
    if (scx_bpf_consume(DSQ_HOT_PATH_USER))    return;
    if (scx_bpf_consume(DSQ_RECOVERY))         return;
    scx_bpf_consume(DSQ_BACKGROUND);
}

s32 BPF_STRUCT_OPS_SLEEPABLE(scx_gaia_init)
{
    // Create named DSQs
    TRY(scx_bpf_create_dsq(DSQ_GUARDIAN_STOP,    -1));
    TRY(scx_bpf_create_dsq(DSQ_NEXUS_BARRIER,    -1));
    TRY(scx_bpf_create_dsq(DSQ_SENSOR_FRESHNESS, -1));
    TRY(scx_bpf_create_dsq(DSQ_HOT_PATH_USER,    -1));
    TRY(scx_bpf_create_dsq(DSQ_BACKGROUND,       -1));
    TRY(scx_bpf_create_dsq(DSQ_RECOVERY,         -1));
    return 0;
}

void BPF_STRUCT_OPS(scx_gaia_exit, struct scx_exit_info *ei)
{
    // On scheduler exit, log reason via BPF trace
    bpf_printk("scx_gaia: exit reason=%llu flags=%llu\n",
               ei->reason, ei->flags);
}

SCX_OPS_DEFINE(scx_gaia_ops,
    .init_task  = (void *)scx_gaia_init_task,
    .enqueue    = (void *)scx_gaia_enqueue,
    .dispatch   = (void *)scx_gaia_dispatch,
    .init       = (void *)scx_gaia_init,
    .exit       = (void *)scx_gaia_exit,
    .name       = "scx_gaia"
);
