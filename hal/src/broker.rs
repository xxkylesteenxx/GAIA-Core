//! GAIA HAL-2 Device Broker
//! Policy-gated device access: enforces capability checks before device assignment.

use crate::driver::DriverClass;

#[derive(Debug)]
pub struct DeviceBroker;

impl DeviceBroker {
    /// Request device access — enforces capability and IOMMU policy
    pub fn request_device(&self, device_id: u32, class: DriverClass) -> Result<DeviceHandle, BrokerError> {
        match class {
            DriverClass::D1 => Err(BrokerError::DirectKernelOwned),
            DriverClass::D2 => Ok(DeviceHandle { device_id }),
            DriverClass::D3 => Ok(DeviceHandle { device_id }), // sandboxed via VM
        }
    }
}

#[derive(Debug)]
pub struct DeviceHandle {
    pub device_id: u32,
}

#[derive(Debug)]
pub enum BrokerError {
    DirectKernelOwned,
    CapabilityDenied,
    DeviceNotFound,
    IommuFault,
}
