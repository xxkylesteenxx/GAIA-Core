//! Consciousness HUD bridge — core status types and sample data.
//!
//! `CoreStatus` carries the health status of a single GAIA core.
//! `sample_core_statuses()` provides a deterministic set for dev/tests.
//!
//! This module is the Rust-side representation of what the TypeScript
//! HUD renders. The IPC layer serialises `Vec<CoreStatus>` into the
//! `HudSnapshot` message sent to the shell.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.4, §6.2

use crate::state::{GaiaCore, OverlayPriority};

/// Health status of a single GAIA core, as presented in the HUD.
#[derive(Debug, Clone)]
pub struct CoreStatus {
    pub core:     GaiaCore,
    pub online:   bool,
    pub summary:  String,
    pub severity: OverlayPriority,
}

impl CoreStatus {
    /// Returns true if this status requires immediate operator attention.
    pub fn requires_operator_attention(&self) -> bool {
        !self.online || self.severity.requires_acknowledgement()
    }
}

/// Deterministic sample core statuses for development and tests.
pub fn sample_core_statuses() -> Vec<CoreStatus> {
    vec![
        CoreStatus {
            core:     GaiaCore::Sophia,
            online:   true,
            summary:  "Knowledge synthesis nominal".to_string(),
            severity: OverlayPriority::Normal,
        },
        CoreStatus {
            core:     GaiaCore::Guardian,
            online:   true,
            summary:  "No active safety violations".to_string(),
            severity: OverlayPriority::Normal,
        },
        CoreStatus {
            core:     GaiaCore::Terra,
            online:   true,
            summary:  "Environmental ingest within target latency".to_string(),
            severity: OverlayPriority::Warning,
        },
    ]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sample_statuses_count() {
        assert_eq!(sample_core_statuses().len(), 3);
    }

    #[test]
    fn terra_warning_does_not_require_attention() {
        let s = sample_core_statuses();
        let terra = s.iter().find(|c| c.core == GaiaCore::Terra).unwrap();
        assert_eq!(terra.severity, OverlayPriority::Warning);
        assert!(!terra.requires_operator_attention());
    }
}
