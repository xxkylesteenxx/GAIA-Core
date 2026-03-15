//! Consciousness HUD bridge — core status types and sample data.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.4, §6.2

use crate::state::{GaiaCore, OverlayPriority};

#[derive(Debug, Clone)]
pub struct CoreStatus {
    pub core:     GaiaCore,
    pub online:   bool,
    pub summary:  String,
    pub severity: OverlayPriority,
}

impl CoreStatus {
    pub fn requires_operator_attention(&self) -> bool {
        !self.online || self.severity.requires_acknowledgement()
    }
}

pub fn sample_core_statuses() -> Vec<CoreStatus> {
    vec![
        CoreStatus { core: GaiaCore::Sophia,   online: true,
            summary:  "Knowledge synthesis nominal".into(),
            severity: OverlayPriority::Normal },
        CoreStatus { core: GaiaCore::Guardian, online: true,
            summary:  "No active safety violations".into(),
            severity: OverlayPriority::Normal },
        CoreStatus { core: GaiaCore::Terra,    online: true,
            summary:  "Environmental ingest within target latency".into(),
            severity: OverlayPriority::Warning },
    ]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn sample_statuses_count() { assert_eq!(sample_core_statuses().len(), 3); }

    #[test]
    fn terra_warning_no_operator_attention() {
        let terra = sample_core_statuses().into_iter()
            .find(|c| c.core == GaiaCore::Terra).unwrap();
        assert!(!terra.requires_operator_attention());
    }
}
