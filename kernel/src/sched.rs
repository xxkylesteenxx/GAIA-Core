//! GAIA Consciousness-Aware Scheduler
//!
//! Layer: L1 — Kernel / Hypervisor Core
//! Subsystem: Scheduler (sched_ext / scx)
//!
//! Implements a sched_ext (scx) scheduler plugin that enforces
//! GAIA's four execution classes:
//!
//!   CCO — Critical Consciousness Operations  (<1ms, non-preemptible by lower classes)
//!   ICO — Interactive Consciousness Operations (<10ms)
//!   ACO — Adaptive Consciousness Operations  (<100ms)
//!   BCO — Background Consciousness Operations (best-effort)
//!
//! CCO/ICO threads (NEXUS, GUARDIAN) are pinned to reserved CPU cores.
//! BCO threads (background indexing, archival) are fully preemptible.

/// Execution class for a GAIA thread.
#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ExecClass {
    CCO = 0, // Critical Consciousness
    ICO = 1, // Interactive Consciousness
    ACO = 2, // Adaptive Consciousness
    BCO = 3, // Background
    AD0 = 4, // User-interactive app work
    AD1 = 5, // App background / batch
}

/// Scheduler state (placeholder — wired to scx ops at build time)
pub struct GaiaSched {
    cco_cores: &'static [usize],
    ico_cores: &'static [usize],
}

impl GaiaSched {
    pub const fn new(cco_cores: &'static [usize], ico_cores: &'static [usize]) -> Self {
        Self { cco_cores, ico_cores }
    }

    /// Select CPU for a task given its execution class.
    pub fn select_cpu(&self, class: ExecClass, prev_cpu: usize) -> usize {
        match class {
            ExecClass::CCO => *self.cco_cores.first().unwrap_or(&0),
            ExecClass::ICO => *self.ico_cores.first().unwrap_or(&prev_cpu),
            _ => prev_cpu, // CFS fallback for ACO/BCO/AD*
        }
    }
}

// Reserved cores (compile-time defaults — overridden by kernel param)
static CCO_CORES: &[usize] = &[0, 1];
static ICO_CORES: &[usize] = &[2, 3];

static SCHEDULER: GaiaSched = GaiaSched::new(CCO_CORES, ICO_CORES);

/// Register the GAIA sched_ext scheduler with the kernel.
pub fn register() -> Result<(), i32> {
    // TODO: wire to scx_ops_register() via kernel FFI
    Ok(())
}

/// Unregister on module exit.
pub fn unregister() {
    // TODO: wire to scx_ops_unregister()
}
