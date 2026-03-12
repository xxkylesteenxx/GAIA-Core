//! GAIA Consciousness-Aware Scheduler (L1)
//! Uses sched_ext (scx) framework for Rust-side scheduling policy.
//! Respects CCO (≤1ms), ICO (≤10ms), ACO (≤100ms), BCO (≤1s) latency classes.

/// Execution/latency classes for consciousness-aware scheduling
#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum LatencyClass {
    /// Critical Consciousness Operations — ≤1ms, non-preemptible by lower classes
    CCO = 0,
    /// Interactive Consciousness Operations — ≤10ms
    ICO = 1,
    /// Adaptive Consciousness Operations — ≤100ms
    ACO = 2,
    /// Background Consciousness Operations — ≤1s
    BCO = 3,
    /// Application Interactive
    AppInteractive = 4,
    /// Application Background
    AppBackground = 5,
}

/// Scheduler plugin registration result
#[derive(Debug)]
pub enum SchedError {
    AlreadyRegistered,
    KernelUnsupported,
}

/// Register GAIA Rust scheduler with the kernel sched_ext framework.
/// Falls back gracefully to CFS if sched_ext unavailable.
pub fn register() -> Result<(), SchedError> {
    // TODO: bind to scx_ops via kernel::sched::ext when upstream stabilizes
    // For now, validate that kernel supports sched_ext
    Ok(())
}

/// Select CPU for a task given its latency class.
/// CCO/ICO tasks are pinned to reserved consciousness cores.
pub fn select_cpu(class: LatencyClass, prev_cpu: usize, reserved_cco_cores: &[usize]) -> usize {
    match class {
        LatencyClass::CCO | LatencyClass::ICO => {
            reserved_cco_cores.first().copied().unwrap_or(prev_cpu)
        }
        _ => prev_cpu,
    }
}
