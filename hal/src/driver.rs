//! GAIA Driver Classification
//! D1: Mandatory kernel (C, boot-critical)
//! D2: GAIA-brokered (Rust, policy-gated)
//! D3: VM-isolated/sandboxed (Rust + rust-vmm)

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DriverClass {
    /// D1: Boot-critical, mandatory kernel — implemented in C
    D1,
    /// D2: GAIA-brokered, policy-gated — implemented in Rust
    D2,
    /// D3: VM-isolated, sandboxed — implemented in Rust + rust-vmm
    D3,
}
