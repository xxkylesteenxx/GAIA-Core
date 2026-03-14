//! GAIA memory isolation policy engine.
//!
//! Spec ref: VIRT-MEM-IPC-SPEC §5
//!
//! Enforces two invariants at region registration time:
//!   1. No two regions for the same domain may overlap in guest physical space.
//!   2. Any shared region MUST carry a label prefixed with `"shared/"` to
//!      make cross-domain access explicit and auditable.

use serde::{Deserialize, Serialize};
use thiserror::Error;

// ── Region descriptor ─────────────────────────────────────────────────────────────

/// A bounded, labeled guest-physical memory region assigned to a domain.
///
/// Spec ref: VIRT-MEM-IPC-SPEC §5
///
/// - Private regions (`shared = false`) are exclusive to `domain`.
/// - Shared regions (`shared = true`) MUST set `label` to a `"shared/"` prefixed
///   string naming the cross-domain purpose, e.g. `"shared/terra-sophia-ringbuf"`.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct MemoryRegion {
    /// Owning domain name.
    pub domain:           String,
    /// Guest physical base address (bytes).
    pub guest_phys_start: u64,
    /// Region size in bytes.
    pub size_bytes:       u64,
    /// Whether this region is a cross-domain shared-memory region.
    pub shared:           bool,
    /// Descriptive label; MUST start with `"shared/"` when `shared = true`.
    pub label:            String,
}

impl MemoryRegion {
    /// Exclusive end address (non-inclusive).
    #[inline]
    pub fn end(&self) -> u64 {
        self.guest_phys_start.saturating_add(self.size_bytes)
    }

    /// Returns `true` if this region overlaps `other` in guest physical space.
    #[inline]
    pub fn overlaps(&self, other: &MemoryRegion) -> bool {
        self.guest_phys_start < other.end() && other.guest_phys_start < self.end()
    }
}

// ── Errors ────────────────────────────────────────────────────────────────────────

#[derive(Debug, Error)]
pub enum MemoryPolicyError {
    #[error(
        "memory region overlap: domain='{domain}' \
         new=[{new_start:#x}, {new_end:#x}) \
         conflicts with [{old_start:#x}, {old_end:#x})"
    )]
    Overlap {
        domain:    String,
        new_start: u64,
        new_end:   u64,
        old_start: u64,
        old_end:   u64,
    },

    #[error("shared region label must start with 'shared/' (got '{label}')")]
    InvalidSharedLabel { label: String },
}

// ── Policy engine ────────────────────────────────────────────────────────────────

/// Memory policy registry for a single domain or the full system.
///
/// `register_region` enforces both overlap-freedom and shared-label
/// discipline at insertion time, so the registry is always consistent.
#[derive(Default, Debug)]
pub struct MemoryPolicy {
    regions: Vec<MemoryRegion>,
}

impl MemoryPolicy {
    pub fn new() -> Self {
        Self::default()
    }

    /// Register a region, enforcing:
    ///   - `"shared/"` label prefix for shared regions (spec §5)
    ///   - no guest-physical overlap with any existing region (spec §5, §9)
    pub fn register_region(&mut self, region: MemoryRegion) -> Result<(), MemoryPolicyError> {
        if region.shared && !region.label.starts_with("shared/") {
            return Err(MemoryPolicyError::InvalidSharedLabel {
                label: region.label.clone(),
            });
        }

        for existing in &self.regions {
            if existing.overlaps(&region) {
                return Err(MemoryPolicyError::Overlap {
                    domain:    region.domain.clone(),
                    new_start: region.guest_phys_start,
                    new_end:   region.end(),
                    old_start: existing.guest_phys_start,
                    old_end:   existing.end(),
                });
            }
        }

        self.regions.push(region);
        Ok(())
    }

    /// Iterate over all registered regions.
    pub fn regions(&self) -> &[MemoryRegion] {
        &self.regions
    }

    pub fn len(&self) -> usize    { self.regions.len() }
    pub fn is_empty(&self) -> bool { self.regions.is_empty() }
}

// ── Tests ──────────────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    fn private_region(domain: &str, start: u64, size: u64) -> MemoryRegion {
        MemoryRegion {
            domain:           domain.into(),
            guest_phys_start: start,
            size_bytes:       size,
            shared:           false,
            label:            String::new(),
        }
    }

    #[test]
    fn register_non_overlapping() {
        let mut policy = MemoryPolicy::new();
        assert!(policy.register_region(private_region("sophia", 0x0000_0000, 0x1000_0000)).is_ok());
        assert!(policy.register_region(private_region("sophia", 0x1000_0000, 0x1000_0000)).is_ok());
        assert_eq!(policy.len(), 2);
    }

    #[test]
    fn reject_overlap() {
        let mut policy = MemoryPolicy::new();
        policy.register_region(private_region("terra", 0x0, 0x2000)).unwrap();
        let result = policy.register_region(private_region("terra", 0x1000, 0x2000));
        assert!(matches!(result, Err(MemoryPolicyError::Overlap { .. })));
    }

    #[test]
    fn shared_region_valid_label() {
        let mut policy = MemoryPolicy::new();
        let region = MemoryRegion {
            domain:           "terra".into(),
            guest_phys_start: 0x8000_0000,
            size_bytes:       0x10_0000,
            shared:           true,
            label:            "shared/terra-sophia-ringbuf".into(),
        };
        assert!(policy.register_region(region).is_ok());
    }

    #[test]
    fn shared_region_invalid_label() {
        let mut policy = MemoryPolicy::new();
        let region = MemoryRegion {
            domain:           "terra".into(),
            guest_phys_start: 0x8000_0000,
            size_bytes:       0x10_0000,
            shared:           true,
            label:            "ringbuf".into(), // missing "shared/" prefix
        };
        assert!(matches!(
            policy.register_region(region),
            Err(MemoryPolicyError::InvalidSharedLabel { .. })
        ));
    }
}
