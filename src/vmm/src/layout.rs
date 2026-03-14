//! GAIA VMM layout loader.
//!
//! Deserializes a TOML domain launch layout into typed Rust structs
//! and validates the configuration before returning it to the caller.
//!
//! Spec ref: VIRT-MEM-IPC-SPEC §5, §9

use anyhow::{bail, Context, Result};
use serde::{Deserialize, Serialize};
use std::fs;

// ── TOML schema types ─────────────────────────────────────────────────────────────

/// Per-domain configuration as declared in the launch layout TOML.
///
/// Maps to `[[domains]]` table entries in `domain_layout_full.toml`.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DomainConfig {
    /// Unique domain name (e.g. `"sophia"`, `"terra"`, `"guardian"`).
    pub name:             String,
    /// Number of virtual CPUs to assign.
    pub vcpu_count:       u8,
    /// Guest RAM in mebibytes.
    pub memory_mib:       u32,
    /// Host path to guest kernel bzImage.
    pub kernel_image:     String,
    /// Optional kernel command line.
    pub cmdline:          Option<String>,
    /// Isolation tier: `"critical"` or `"bounded"`.
    pub protection_class: String,
}

impl DomainConfig {
    /// Validate the config before any KVM resources are allocated.
    /// Spec ref: VIRT-MEM-IPC-SPEC §9 — VM launch policy conformance.
    pub fn validate(&self) -> Result<()> {
        if self.name.is_empty() {
            bail!("domain name must not be empty");
        }
        if self.vcpu_count == 0 {
            bail!("domain '{}': vcpu_count must be >= 1", self.name);
        }
        if self.memory_mib == 0 {
            bail!("domain '{}': memory_mib must be > 0", self.name);
        }
        match self.protection_class.as_str() {
            "critical" | "bounded" => {}
            other => bail!(
                "domain '{}': unknown protection_class '{}' (expected 'critical' or 'bounded')",
                self.name, other
            ),
        }
        Ok(())
    }

    /// Guest RAM in bytes.
    pub fn memory_bytes(&self) -> u64 {
        self.memory_mib as u64 * 1024 * 1024
    }
}

/// Top-level launch layout — deserializes the full TOML file.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LaunchLayout {
    pub domains: Vec<DomainConfig>,
}

impl LaunchLayout {
    /// Validate all domain configs.
    pub fn validate(&self) -> Result<()> {
        if self.domains.is_empty() {
            bail!("launch layout contains no domains");
        }
        for domain in &self.domains {
            domain.validate()?;
        }
        Ok(())
    }
}

// ── Loader ────────────────────────────────────────────────────────────────────────

/// Read, parse, and validate a TOML launch layout file.
pub fn load_layout(path: &str) -> Result<LaunchLayout> {
    let raw = fs::read_to_string(path)
        .with_context(|| format!("failed to read layout file: {path}"))?;

    let layout: LaunchLayout = toml::from_str(&raw)
        .with_context(|| format!("failed to parse layout file: {path}"))?;

    layout.validate()
        .with_context(|| format!("layout validation failed: {path}"))?;

    Ok(layout)
}

// ── Tests ──────────────────────────────────────────────────────────────────────────

#[cfg(test)]
mod tests {
    use super::*;

    fn valid_domain() -> DomainConfig {
        DomainConfig {
            name:             "test".into(),
            vcpu_count:       2,
            memory_mib:       512,
            kernel_image:     "/boot/bzImage".into(),
            cmdline:          None,
            protection_class: "critical".into(),
        }
    }

    #[test]
    fn domain_validate_ok() {
        assert!(valid_domain().validate().is_ok());
    }

    #[test]
    fn domain_zero_vcpus_rejected() {
        let mut d = valid_domain();
        d.vcpu_count = 0;
        assert!(d.validate().is_err());
    }

    #[test]
    fn domain_zero_memory_rejected() {
        let mut d = valid_domain();
        d.memory_mib = 0;
        assert!(d.validate().is_err());
    }

    #[test]
    fn domain_unknown_class_rejected() {
        let mut d = valid_domain();
        d.protection_class = "unchecked".into();
        assert!(d.validate().is_err());
    }

    #[test]
    fn parse_inline_toml() {
        let src = r#"
[[domains]]
name             = "sophia"
vcpu_count       = 2
memory_mib       = 2048
kernel_image     = "/var/lib/gaia/guests/sophia/bzImage"
protection_class = "critical"
"#;
        let layout: LaunchLayout = toml::from_str(src).unwrap();
        assert_eq!(layout.domains.len(), 1);
        assert!(layout.validate().is_ok());
    }
}
