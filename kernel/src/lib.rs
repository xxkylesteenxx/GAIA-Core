//! GAIA L1 Kernel — Rust-first core
//! Layer: L1 (Kernel / Hypervisor Core)
//! Languages: Rust (first), C (second), Assembly (stubs)
//! See: docs/specs/platform/GAIALanguageStackSpecv1.0.md

#![no_std]
#![allow(unused)]

extern crate alloc;

pub mod sched;
pub mod ipc;
pub mod caps;
pub mod virt;

/// GAIA kernel initialization entry point (called from C init)
/// Registers Rust-side scheduler, IPC primitives, and capability framework.
#[no_mangle]
pub extern "C" fn gaia_kernel_init() -> i32 {
    if sched::register().is_err() { return -1; }
    if ipc::init().is_err() { return -1; }
    if caps::init().is_err() { return -1; }
    0 // success
}
