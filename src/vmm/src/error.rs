use thiserror::Error;

#[derive(Debug, Error)]
pub enum VmmError {
    #[error("KVM unavailable: {0}")]
    KvmUnavailable(String),

    #[error("VM creation failed: {0}")]
    VmCreateFailed(String),

    #[error("vCPU error: {0}")]
    VcpuError(String),

    #[error("memory region overlap detected")]
    MemoryOverlap,

    #[error("launch policy violation: {0}")]
    LaunchPolicyViolation(String),

    #[error("domain not found: {0}")]
    DomainNotFound(String),
}
