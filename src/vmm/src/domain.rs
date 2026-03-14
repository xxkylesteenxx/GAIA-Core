//! Domain lifecycle model.
//! Spec ref: VIRT-MEM-IPC-SPEC §3.1, §4, §9

use crate::error::VmmError;

/// Lifecycle state of a GAIA protected domain.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum DomainState {
    Defined,
    Launching,
    Running,
    Paused,
    Shutdown,
    Error(String),
}

/// Static configuration for a domain at launch time.
#[derive(Debug, Clone)]
pub struct DomainConfig {
    pub name:         String,
    pub vcpu_count:   u32,
    pub memory_bytes: u64,
    /// Workload class (mirrors gaia_workload_class from platform layer).
    pub workload_class: u32,
}

/// A GAIA protected domain — one isolation boundary.
#[derive(Debug)]
pub struct Domain {
    pub config: DomainConfig,
    pub state:  DomainState,
    // vm_fd: KvmVm,  // uncomment when linking kvm-ioctls
}

impl Domain {
    pub fn new(config: DomainConfig) -> Self {
        Self {
            config,
            state: DomainState::Defined,
        }
    }

    /// Validate launch policy before creating VM resources.
    /// Spec ref: §9 — VM launch policy conformance.
    pub fn validate_launch(&self) -> Result<(), VmmError> {
        if self.config.vcpu_count == 0 {
            return Err(VmmError::LaunchPolicyViolation(
                "vcpu_count must be >= 1".into(),
            ));
        }
        if self.config.memory_bytes == 0 {
            return Err(VmmError::LaunchPolicyViolation(
                "memory_bytes must be > 0".into(),
            ));
        }
        Ok(())
    }

    pub fn transition(&mut self, next: DomainState) {
        log::info!(
            "domain '{}': {:?} -> {:?}",
            self.config.name, self.state, next
        );
        self.state = next;
    }
}
