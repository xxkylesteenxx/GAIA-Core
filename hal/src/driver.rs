//! GAIA HAL-2 Device Broker
//!
//! Layer: L2 — HAL / Drivers
//! Language: Rust
//!
//! The HAL-2 broker mediates all device access between the kernel
//! and user-space services. It enforces:
//!   - IOMMU-safe device assignment
//!   - Device class policy (D1/D2/D3)
//!   - Capability-gated access (P0–P3)
//!   - Audit logging for every device open/close

/// Device class in the GAIA driver model.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum DeviceClass {
    D1Mandatory,   // Boot-critical (storage/net/display) — C drivers
    D2Brokered,    // Standard peripherals — Rust drivers, broker-mediated
    D3Isolated,    // Untrusted / VM-isolated — Rust, sandboxed
}

/// A registered device entry in the HAL-2 broker.
#[derive(Debug)]
pub struct DeviceEntry {
    pub id: u64,
    pub class: DeviceClass,
    pub iommu_group: u32,
    pub driver_name: &'static str,
}

/// The HAL-2 broker registry (placeholder — backed by kernel table at runtime).
pub struct GaiaBroker {
    // TODO: replace with kernel-backed registry via FFI
    devices: [Option<DeviceEntry>; 64],
}

impl GaiaBroker {
    pub const fn new() -> Self {
        const NONE: Option<DeviceEntry> = None;
        Self { devices: [NONE; 64] }
    }

    /// Register a device with the broker.
    pub fn register(&mut self, entry: DeviceEntry) -> Result<(), &'static str> {
        for slot in self.devices.iter_mut() {
            if slot.is_none() {
                *slot = Some(entry);
                return Ok(());
            }
        }
        Err("HAL-2 broker: device table full")
    }

    /// Look up a device by ID.
    pub fn lookup(&self, id: u64) -> Option<&DeviceEntry> {
        self.devices.iter()
            .filter_map(|s| s.as_ref())
            .find(|d| d.id == id)
    }
}
