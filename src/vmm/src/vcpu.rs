//! vCPU handle placeholder.
//! Spec ref: VIRT-MEM-IPC-SPEC §3.2, §9

use crate::error::VmmError;

#[derive(Debug)]
pub struct VcpuHandle {
    pub id: u32,
    // vcpu_fd: KvmVcpu,  // uncomment when linking kvm-ioctls
}

impl VcpuHandle {
    pub fn new(id: u32) -> Result<Self, VmmError> {
        // TODO: open /dev/kvm, create VM fd, create vCPU fd
        Ok(Self { id })
    }
}
