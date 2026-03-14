//! Consciousness HUD state types and sample data.
//!
//! `CoreStatus` carries the health status of a single GAIA core as
//! displayed in the Consciousness HUD. `sample_core_statuses()` provides
//! a deterministic set of statuses for development and tests.
//!
//! HUD alert state taxonomy (spec §6.2):
//!   Normal   — nominal; no indicator
//!   Info     — informational; blue tone; auto-dismisses
//!   Warning  — amber tone; persists until acknowledged
//!   Critical — red tone; modal; operator action required
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.4, §6.2

use crate::state::{GaiaCore, OverlayPriority};

/// Health status of a single GAIA core, as presented in the HUD.
#[derive(Debug, Clone)]
pub struct CoreStatus {
    /// The GAIA core this status record describes.
    pub core:     GaiaCore,
    /// Whether the core is currently reachable and operational.
    pub online:   bool,
    /// Short human-readable summary for the HUD status row.
    pub summary:  String,
    /// Alert severity tier for the HUD visual indicator.
    pub severity: OverlayPriority,
}

impl CoreStatus {
    /// Returns true if this status requires immediate operator attention.
    ///
    /// Operator attention is required for any offline core or any
    /// core with Critical severity.
    pub fn requires_operator_attention(&self) -> bool {
        !self.online || self.severity.requires_acknowledgement()
    }
}

/// Return a deterministic sample set of core statuses for dev / tests.
///
/// Covers the three primary HUD-visible cores (SOPHIA, GUARDIAN, TERRA)
/// with mixed severity to exercise all visual indicator states.
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
        let statuses = sample_core_statuses();
        assert_eq!(statuses.len(), 3);
    }

    #[test]
    fn sophia_and_guardian_are_nominal() {
        let statuses = sample_core_statuses();
        for s in statuses.iter().filter(|s| {
            matches!(s.core, GaiaCore::Sophia | GaiaCore::Guardian)
        }) {
            assert_eq!(s.severity, OverlayPriority::Normal);
            assert!(s.online);
            assert!(!s.requires_operator_attention());
        }
    }

    #[test]
    fn terra_has_warning_severity() {
        let statuses = sample_core_statuses();
        let terra = statuses.iter().find(|s| s.core == GaiaCore::Terra).unwrap();
        assert_eq!(terra.severity, OverlayPriority::Warning);
        assert!(!terra.requires_operator_attention()); // Warning, not Critical
    }

    #[test]
    fn offline_core_requires_attention() {
        let status = CoreStatus {
            core:     GaiaCore::Atlas,
            online:   false,
            summary:  "Infrastructure core unreachable".to_string(),
            severity: OverlayPriority::Critical,
        };
        assert!(status.requires_operator_attention());
    }
}
