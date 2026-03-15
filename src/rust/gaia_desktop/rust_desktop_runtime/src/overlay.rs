//! Overlay z-band enforcement and safety overlay policy.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.2, §4.2

use crate::state::{DesktopState, GaiaCore, OverlayPriority, OverlayRecord};

#[derive(Debug, PartialEq, Eq)]
pub enum OverlayError {
    ZBandViolation { surface_id: u64, requested: String },
    NotFound(String),
    AutoDismissBlocked(String),
}

impl std::fmt::Display for OverlayError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            OverlayError::ZBandViolation { surface_id, requested } =>
                write!(f, "z-band violation: surface {surface_id} → '{requested}'"),
            OverlayError::NotFound(id) =>
                write!(f, "overlay not found: {id}"),
            OverlayError::AutoDismissBlocked(id) =>
                write!(f, "automated dismissal of blocking overlay '{id}' not permitted"),
        }
    }
}

pub struct OverlayManager;

impl OverlayManager {
    /// Register a new overlay. String `id` is the stable upsert key.
    pub fn register_overlay(
        state:    &mut DesktopState,
        id:       impl Into<String>,
        owner:    GaiaCore,
        priority: OverlayPriority,
        message:  impl Into<String>,
    ) {
        let id = id.into();
        if let Some(existing) = state.overlays.iter_mut().find(|o| o.id == id) {
            existing.priority = priority;
            existing.visible  = true;
            existing.message  = message.into();
            existing.owner    = owner;
        } else {
            state.overlays.push(OverlayRecord {
                id, owner, priority, visible: true, message: message.into(),
            });
        }
    }

    /// Assert an untrusted surface is not raising into a system z-band (DSK-009).
    pub fn assert_zband_safe(surface_id: u64, requested_band: &str) -> Result<(), OverlayError> {
        const SYSTEM_BANDS: &[&str] = &["critical", "safety", "guardian", "system"];
        if SYSTEM_BANDS.contains(&requested_band.to_lowercase().as_str()) {
            return Err(OverlayError::ZBandViolation {
                surface_id, requested: requested_band.to_owned(),
            });
        }
        Ok(())
    }

    /// Dismiss overlay by string id.
    /// Critical overlays require `operator_confirmed = true` (spec §6.2).
    pub fn dismiss_overlay(
        state:              &mut DesktopState,
        id:                 &str,
        operator_confirmed: bool,
    ) -> Result<(), OverlayError> {
        let overlay = state.overlays.iter_mut().find(|o| o.id == id)
            .ok_or_else(|| OverlayError::NotFound(id.to_owned()))?;
        if matches!(overlay.priority, OverlayPriority::Critical) && !operator_confirmed {
            return Err(OverlayError::AutoDismissBlocked(id.to_owned()));
        }
        overlay.visible = false;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::state::DesktopState;

    #[test]
    fn zband_violation_detected() {
        assert!(OverlayManager::assert_zband_safe(1, "critical").is_err());
    }

    #[test]
    fn app_zband_allowed() {
        OverlayManager::assert_zband_safe(1, "app").unwrap();
    }

    #[test]
    fn auto_dismiss_critical_blocked() {
        let mut state = DesktopState::default();
        OverlayManager::register_overlay(
            &mut state, "g", GaiaCore::Guardian, OverlayPriority::Critical, "test",
        );
        assert!(OverlayManager::dismiss_overlay(&mut state, "g", false).is_err());
    }

    #[test]
    fn operator_dismiss_critical_succeeds() {
        let mut state = DesktopState::default();
        OverlayManager::register_overlay(
            &mut state, "g", GaiaCore::Guardian, OverlayPriority::Critical, "test",
        );
        OverlayManager::dismiss_overlay(&mut state, "g", true).unwrap();
        assert!(!state.overlays[0].visible);
    }
}
