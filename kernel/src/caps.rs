//! GAIA Capability and Security Primitives (L1)
//! Rust-side capability framework: least-privilege tokens for kernel resources.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Capability {
    /// Access to consciousness core state
    ConsciousnessRead,
    ConsciousnessWrite,
    /// Scheduler policy override
    SchedPolicy,
    /// Device access
    DeviceAccess(u32),
    /// Network egress
    NetworkEgress,
    /// VM lifecycle management
    VmControl,
}

/// Capability token — unforgeable, checked at every privileged boundary
#[derive(Debug)]
pub struct CapToken {
    pub cap: Capability,
    pub subject_pid: u32,
    pub granted_by: u32,
}

/// Initialize GAIA capability framework
pub fn init() -> Result<(), CapsError> {
    // TODO: register GAIA LSM hooks for capability enforcement
    Ok(())
}

#[derive(Debug)]
pub enum CapsError {
    InitFailed,
    Denied,
}
