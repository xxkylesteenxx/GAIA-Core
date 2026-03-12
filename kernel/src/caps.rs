//! GAIA Capability Primitives
//!
//! Layer: L1 — Kernel / Hypervisor Core
//! Subsystem: Capabilities / Security
//!
//! Provides the GAIA capability table and LSM hooks used by GUARDIAN.
//! Every GAIA service is assigned a capability class:
//!
//!   P0 — Kernel/firmware (unrestricted)
//!   P1 — Privileged platform services (NEXUS, GUARDIAN, SOPHIA)
//!   P2 — Trusted first-party services (ATLAS, Gaian)
//!   P3 — Third-party apps (sandboxed, GAPI broker only)

/// GAIA privilege class.
#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum PrivClass {
    P0Kernel    = 0,
    P1Platform  = 1,
    P2Trusted   = 2,
    P3App       = 3,
}

/// Capability entry for a GAIA process.
#[derive(Debug, Clone)]
pub struct GaiaCapability {
    pub class: PrivClass,
    pub can_ipc_direct: bool,
    pub can_syscall_raw: bool,
    pub can_access_consciousness: bool,
}

impl GaiaCapability {
    pub const fn for_class(class: PrivClass) -> Self {
        match class {
            PrivClass::P0Kernel => Self {
                class,
                can_ipc_direct: true,
                can_syscall_raw: true,
                can_access_consciousness: true,
            },
            PrivClass::P1Platform => Self {
                class,
                can_ipc_direct: true,
                can_syscall_raw: false,
                can_access_consciousness: true,
            },
            PrivClass::P2Trusted => Self {
                class,
                can_ipc_direct: false,
                can_syscall_raw: false,
                can_access_consciousness: false,
            },
            PrivClass::P3App => Self {
                class,
                can_ipc_direct: false,
                can_syscall_raw: false,
                can_access_consciousness: false,
            },
        }
    }
}

/// Initialize capability tables.
pub fn init() -> Result<(), i32> {
    // TODO: register capability table with GUARDIAN LSM hook
    Ok(())
}
