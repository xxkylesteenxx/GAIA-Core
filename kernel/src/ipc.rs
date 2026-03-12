//! GAIA IPC Primitives (L1)
//! Safe Rust wrappers over kernel IPC: mailboxes, ring buffers, capability channels.

/// IPC initialization — registers GAIA-specific IPC endpoints with the kernel.
pub fn init() -> Result<(), IpcError> {
    // TODO: register GAIA IPC namespaces, bounded mailboxes, and cap channels
    Ok(())
}

#[derive(Debug)]
pub enum IpcError {
    InitFailed,
    CapabilityDenied,
    BufferFull,
}

/// Bounded mailbox for inter-core messaging
pub struct BoundedMailbox<T, const N: usize> {
    // ring buffer: single-writer, single-reader, lock-free
    _marker: core::marker::PhantomData<T>,
}

impl<T, const N: usize> BoundedMailbox<T, N> {
    pub const fn new() -> Self {
        Self { _marker: core::marker::PhantomData }
    }
}
