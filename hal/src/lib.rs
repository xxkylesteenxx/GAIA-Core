//! GAIA L2 HAL — Hardware Abstraction Layer
//! Layer: L2 (HAL / Drivers)
//! Rust-first: new drivers, HAL-1/2 brokers, IOMMU policy
//! C: D1 mandatory (boot-critical) drivers only
//! See: docs/specs/platform/GAIALanguageStackSpecv1.0.md

#![no_std]

extern crate alloc;

pub mod broker;
pub mod iommu;
pub mod driver;
