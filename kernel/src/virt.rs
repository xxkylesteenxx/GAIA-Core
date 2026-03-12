//! GAIA Virtualization Hooks (L1)
//! Rust-side KVM integration: guest lifecycle, vCPU management, isolation boundaries.

/// Guest VM descriptor
#[derive(Debug)]
pub struct GaiaVm {
    pub vm_id: u32,
    pub vcpu_count: u8,
    pub trust_class: VmTrustClass,
}

#[derive(Debug, Clone, Copy)]
pub enum VmTrustClass {
    /// Fully attested GAIA guest
    Trusted,
    /// Partially attested, limited capabilities
    Restricted,
    /// Unverified third-party guest
    Sandboxed,
}

/// Initialize KVM hooks for GAIA VM lifecycle management
pub fn init_kvm_hooks() -> Result<(), VirtError> {
    // TODO: bind to KVM notifiers via kernel::kvm when available
    Ok(())
}

#[derive(Debug)]
pub enum VirtError {
    KvmUnavailable,
    InitFailed,
}
