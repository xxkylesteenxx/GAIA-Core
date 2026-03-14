//! Overlay z-band enforcement and safety overlay policy.
//!
//! Owns:
//!   - Overlay surface registration with priority tier assignment
//!   - Z-band enforcement: Critical overlays preempt all app chrome (DSK-005)
//!   - Safety overlay non-spoofability: untrusted surfaces cannot
//!     raise into system z-bands (DSK-009)
//!   - Overlay visibility and dismissal (blocking alerts require
//!     explicit operator action — see §6.2 of the spec)
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.2, §4.2

use crate::state::{DesktopState, OverlayPriority, OverlayRecord};

/// Error type for overlay operations.
#[derive(Debug, PartialEq, Eq)]
pub enum OverlayError {
    /// Surface attempted to set z-order above permitted z-band.
    ZBandViolation { surface_id: u64, requested: String },
    /// Overlay id not found.
    NotFound(u64),
    /// Attempted automated dismissal of a blocking-class overlay.
    AutoDismissBlocked(u64),
}

impl std::fmt::Display for OverlayError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            OverlayError::ZBandViolation { surface_id, requested } =>
                write!(f, "z-band violation: surface {surface_id} attempted to raise into '{requested}' z-band"),
            OverlayError::NotFound(id) =>
                write!(f, "overlay not found: {id}"),
            OverlayError::AutoDismissBlocked(id) =>
                write!(f, "automated dismissal of blocking overlay {id} is not permitted"),
        }
    }
}

/// Overlay policy engine.
pub struct OverlayManager {
    next_overlay_id: u64,
}

impl Default for OverlayManager {
    fn default() -> Self {
        Self { next_overlay_id: 1 }
    }
}

impl OverlayManager {
    /// Register a new overlay surface with the given priority.
    ///
    /// Only trusted runtime code may call this function — the IPC
    /// layer SHALL NOT expose this call to untrusted application clients
    /// (DSK-009: safety overlays are non-spoofable).
    pub fn register_overlay(
        &mut self,
        state: &mut DesktopState,
        label: impl Into<String>,
        priority: OverlayPriority,
    ) -> u64 {
        let id = self.next_overlay_id;
        self.next_overlay_id += 1;
        state.overlays.push(OverlayRecord {
            id,
            label: label.into(),
            priority,
            visible: true,
        });
        id
    }

    /// Assert that an untrusted surface is not raising into a system z-band.
    ///
    /// Call this at every client z-order request. Returns
    /// `Err(OverlayError::ZBandViolation)` if the surface attempts to
    /// enter a reserved system z-band (DSK-009).
    pub fn assert_zband_safe(
        surface_id: u64,
        requested_band: &str,
    ) -> Result<(), OverlayError> {
        const SYSTEM_BANDS: &[&str] = &["critical", "safety", "guardian", "system"];
        if SYSTEM_BANDS.contains(&requested_band.to_lowercase().as_str()) {
            return Err(OverlayError::ZBandViolation {
                surface_id,
                requested: requested_band.to_owned(),
            });
        }
        Ok(())
    }

    /// Dismiss an overlay.
    ///
    /// Critical-priority overlays require `operator_confirmed = true`.
    /// Passing `false` for a Critical overlay returns
    /// `Err(OverlayError::AutoDismissBlocked)` — automated agents
    /// SHALL NOT dismiss blocking-class alerts (spec §6.2).
    pub fn dismiss_overlay(
        &self,
        state: &mut DesktopState,
        overlay_id: u64,
        operator_confirmed: bool,
    ) -> Result<(), OverlayError> {
        let overlay = state
            .overlays
            .iter_mut()
            .find(|o| o.id == overlay_id)
            .ok_or(OverlayError::NotFound(overlay_id))?;

        if matches!(overlay.priority, OverlayPriority::Critical) && !operator_confirmed {
            return Err(OverlayError::AutoDismissBlocked(overlay_id));
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
        let err = OverlayManager::assert_zband_safe(42, "critical").unwrap_err();
        assert!(matches!(err, OverlayError::ZBandViolation { .. }));
    }

    #[test]
    fn normal_zband_allowed() {
        OverlayManager::assert_zband_safe(42, "app").unwrap();
    }

    #[test]
    fn auto_dismiss_critical_blocked() {
        let mut state = DesktopState::default();
        let mut mgr = OverlayManager::default();
        let id = mgr.register_overlay(&mut state, "GUARDIAN", OverlayPriority::Critical);
        let err = mgr.dismiss_overlay(&mut state, id, false).unwrap_err();
        assert_eq!(err, OverlayError::AutoDismissBlocked(id));
    }

    #[test]
    fn operator_dismiss_critical_succeeds() {
        let mut state = DesktopState::default();
        let mut mgr = OverlayManager::default();
        let id = mgr.register_overlay(&mut state, "GUARDIAN", OverlayPriority::Critical);
        mgr.dismiss_overlay(&mut state, id, true).unwrap();
        assert!(!state.overlays.iter().find(|o| o.id == id).unwrap().visible);
    }
}
