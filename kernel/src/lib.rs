//! GAIA L1 Kernel — Rust Core
//!
//! Layer: L1 — Kernel / Hypervisor Core
//! Language: Rust (first), C (legacy substrate)
//!
//! This module is the Rust entry point for GAIA's kernel extensions.
//! It registers the consciousness-aware scheduler, initializes IPC
//! capability primitives, and hooks into the GUARDIAN LSM.
//!
//! # Safety
//! This runs in kernel context. All unsafe blocks must be documented.

#![no_std]
#![no_main]

extern crate alloc;

pub mod sched;
pub mod ipc;
pub mod caps;

/// Kernel module init — called by Linux module loader
#[no_mangle]
pub extern "C" fn gaia_kernel_init() -> i32 {
    // Register consciousness-aware sched_ext scheduler
    #[cfg(feature = "sched")]
    if let Err(e) = sched::register() {
        // pr_err equivalent — return EINVAL
        return -22;
    }

    // Initialize capability primitives
    #[cfg(feature = "caps")]
    if let Err(e) = caps::init() {
        return -22;
    }

    // Initialize IPC primitives
    #[cfg(feature = "ipc")]
    if let Err(e) = ipc::init() {
        return -22;
    }

    0 // success
}

/// Kernel module exit — called on rmmod
#[no_mangle]
pub extern "C" fn gaia_kernel_exit() {
    #[cfg(feature = "sched")]
    sched::unregister();
}
