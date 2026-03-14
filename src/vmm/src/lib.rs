//! GAIA VMM — Rust-first KVM control plane skeleton.
//!
//! Spec ref: VIRT-MEM-IPC-SPEC §3.1, §4, §9

pub mod domain;
pub mod error;
pub mod vcpu;

pub use domain::{Domain, DomainConfig, DomainState};
pub use error::VmmError;
