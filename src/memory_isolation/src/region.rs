//! Memory region descriptor.
//! Spec ref: VIRT-MEM-IPC-SPEC §5

/// Classification of a memory region.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RegionKind {
    /// Exclusive to one domain — no cross-domain access.
    Private,
    /// Explicitly shared between named domains, opt-in only.
    Shared { label: String },
}

/// A bounded, labeled memory region assigned to a domain.
#[derive(Debug, Clone)]
pub struct MemoryRegion {
    pub domain:      String,
    pub guest_phys:  u64,
    pub size_bytes:  u64,
    pub kind:        RegionKind,
}

impl MemoryRegion {
    pub fn end(&self) -> u64 {
        self.guest_phys.saturating_add(self.size_bytes)
    }

    /// Returns true if this region overlaps with `other` (same domain scope).
    pub fn overlaps(&self, other: &MemoryRegion) -> bool {
        self.guest_phys < other.end() && other.guest_phys < self.end()
    }
}
