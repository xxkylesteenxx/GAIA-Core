//! GAIA vCPU management — guest CPU virtualization
//! Handles: vCPU creation, execution loop, exit handling, snapshot/restore

use kvm_ioctls::{VcpuExit, VcpuFd, VmFd};

/// GAIA vCPU wrapper with trust classification
pub struct GaiaVcpu {
    pub fd: VcpuFd,
    pub id: u8,
}

impl GaiaVcpu {
    pub fn new(vm: &VmFd, id: u8) -> Result<Self, VcpuError> {
        let fd = vm.create_vcpu(id as u64).map_err(|_| VcpuError::CreateFailed)?;
        Ok(Self { fd, id })
    }

    /// Run vCPU execution loop — handles VM exits
    pub fn run(&self) -> Result<(), VcpuError> {
        loop {
            match self.fd.run().map_err(|_| VcpuError::RunFailed)? {
                VcpuExit::Hlt => break,
                VcpuExit::IoIn(_, _) | VcpuExit::IoOut(_, _, _, _) => {
                    // Handle virtio/device IO
                }
                _ => {}
            }
        }
        Ok(())
    }
}

#[derive(Debug)]
pub enum VcpuError {
    CreateFailed,
    RunFailed,
    SnapshotFailed,
    RestoreFailed,
}
