//! GAIA IPC Primitives
//!
//! Layer: L1 — Kernel / Hypervisor Core
//! Subsystem: Inter-Process Communication
//!
//! Provides the foundation for GAIA's three-tier IPC fabric:
//!   Tier 1 — memfd zero-copy shared memory (intra-host, same security domain)
//!   Tier 2 — io_uring async I/O (high-throughput async messaging)
//!   Tier 3 — gRPC/Protobuf over Unix sockets (cross-domain, cross-host)
//!
//! This module initializes kernel-side IPC bookkeeping and capability gates.

/// IPC tier classification.
#[repr(u8)]
#[derive(Debug, Clone, Copy)]
pub enum IpcTier {
    SharedMemory = 1, // memfd zero-copy
    AsyncIo      = 2, // io_uring
    RpcSock      = 3, // gRPC/Protobuf over Unix socket
}

/// Initialize IPC primitives at kernel module load.
pub fn init() -> Result<(), i32> {
    // TODO: register GAIA IPC capability gates with GUARDIAN LSM
    // TODO: initialize memfd policy table
    // TODO: set up io_uring submission queue bookkeeping
    Ok(())
}
