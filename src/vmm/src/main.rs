//! GAIA VMM entry point.
//!
//! Loads a TOML domain launch layout, validates it, and drives
//! the GaiaVmm to create each domain in order.
//!
//! Usage:
//!   cargo run -p gaia-vmm -- examples/domain_layout_full.toml

mod domain;
mod error;
mod layout;
mod vcpu;

use anyhow::Result;
use layout::{GaiaVmm, load_layout};

fn main() -> Result<()> {
    env_logger::try_init().ok();

    let path = std::env::args()
        .nth(1)
        .unwrap_or_else(|| "examples/domain_layout_full.toml".to_string());

    log::info!("[gaia-vmm] loading layout: {path}");
    let layout = load_layout(&path)?;

    let vmm = GaiaVmm::new();
    vmm.launch_layout(&layout)?;

    Ok(())
}
