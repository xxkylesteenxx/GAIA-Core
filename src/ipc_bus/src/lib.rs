//! GAIA inter-core IPC bus.
//!
//! Spec ref: VIRT-MEM-IPC-SPEC §3.4, §6

pub mod endpoint;
pub mod route;
pub mod message;

pub use endpoint::Endpoint;
pub use route::{RouteTable, RouteError};
pub use message::{Message, MessageClass};
