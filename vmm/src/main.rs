//! GAIA L3 VMM — Rust-first hypervisor
//! Layer: L3 (Hypervisor / VMM / Guest Execution)
//! Built on: rust-vmm crates (kvm-ioctls, vm-memory, vmm-sys-util)
//! See: docs/specs/platform/GAIALanguageStackSpecv1.0.md

use kvm_ioctls::Kvm;

pub mod vcpu;
pub mod memory;
pub mod devices;
pub mod snapshot;

fn main() {
    let kvm = Kvm::new().expect("GAIA VMM: KVM not available");
    let api_version = kvm.get_api_version();
    println!("GAIA VMM: KVM API version {api_version}");

    // TODO: parse VM config, create VM, attach virtio devices, start vCPUs
    println!("GAIA VMM: Rust-first hypervisor initialized");
}
