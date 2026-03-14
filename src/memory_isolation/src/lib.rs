//! GAIA memory isolation layer.
//!
//! Spec ref: VIRT-MEM-IPC-SPEC §3.3, §5

pub mod region;
pub mod map;

pub use region::{MemoryRegion, RegionKind};
pub use map::{RegionMap, RegionMapError};
