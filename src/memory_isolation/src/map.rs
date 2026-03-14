//! Region map — tracks all registered regions and enforces non-overlap.
//! Spec ref: VIRT-MEM-IPC-SPEC §5, §9

use crate::region::MemoryRegion;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum RegionMapError {
    #[error("region overlap detected for domain '{0}' at gpa {1:#x}")]
    Overlap(String, u64),
}

#[derive(Debug, Default)]
pub struct RegionMap {
    regions: Vec<MemoryRegion>,
}

impl RegionMap {
    pub fn new() -> Self { Self::default() }

    /// Register a region, rejecting it if it overlaps an existing one.
    /// Spec ref: §9 — memory region registration and non-overlap.
    pub fn register(&mut self, region: MemoryRegion) -> Result<(), RegionMapError> {
        for existing in &self.regions {
            if existing.domain == region.domain && existing.overlaps(&region) {
                return Err(RegionMapError::Overlap(
                    region.domain.clone(),
                    region.guest_phys,
                ));
            }
        }
        self.regions.push(region);
        Ok(())
    }

    pub fn iter(&self) -> impl Iterator<Item = &MemoryRegion> {
        self.regions.iter()
    }

    pub fn len(&self) -> usize { self.regions.len() }
    pub fn is_empty(&self) -> bool { self.regions.is_empty() }
}
