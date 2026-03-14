//! Compositor facade — surface lifecycle and focus auditability.
//!
//! Owns:
//!   - Surface registration and destruction
//!   - Focus assignment and focus audit log (DSK-008)
//!   - Critical-overlay gate for normal surface presentation (DSK-005)
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.1, §4.1

use crate::state::{DesktopState, OverlayPriority, SurfaceRecord};

/// Compositor facade.
///
/// Holds per-instance mutable state (surface ID counter).
/// `DesktopState` is passed by mutable reference so the single
/// source of truth lives in the runtime event loop.
pub struct CompositorFacade {
    next_surface_id: u64,
}

impl Default for CompositorFacade {
    fn default() -> Self {
        Self { next_surface_id: 1 }
    }
}

impl CompositorFacade {
    /// Register a new surface and insert it into desktop state.
    ///
    /// Returns the assigned surface id. The surface starts unfocused.
    pub fn register_surface(
        &mut self,
        state: &mut DesktopState,
        app_id: impl Into<String>,
        title: impl Into<String>,
        workspace: usize,
        floating: bool,
    ) -> u64 {
        let id = self.next_surface_id;
        self.next_surface_id += 1;
        let record = SurfaceRecord {
            id,
            app_id: app_id.into(),
            title: title.into(),
            workspace,
            focused: false,
            floating,
        };
        state.surfaces.insert(id, record);
        state.workspace_focus.entry(workspace).or_insert(None);
        id
    }

    /// Destroy a surface and clear any focus it held.
    ///
    /// Records a focus-loss audit entry if the surface was focused (DSK-008).
    pub fn destroy_surface(
        &self,
        state: &mut DesktopState,
        surface_id: u64,
    ) -> Result<(), String> {
        let record = state
            .surfaces
            .remove(&surface_id)
            .ok_or_else(|| format!("unknown surface: {surface_id}"))?;
        if record.focused {
            state.record_focus_event(surface_id, false);
            state.workspace_focus.insert(record.workspace, None);
        }
        Ok(())
    }

    /// Assign input focus to a surface.
    ///
    /// Clears focus from all other surfaces, updates workspace_focus
    /// and active_workspace, and appends immutable audit entries (DSK-008):
    /// one focus-loss entry per previously focused surface, one
    /// focus-gain entry for the newly focused surface.
    pub fn focus_surface(
        &self,
        state: &mut DesktopState,
        surface_id: u64,
    ) -> Result<(), String> {
        let workspace = state
            .surfaces
            .get(&surface_id)
            .ok_or_else(|| format!("unknown surface: {surface_id}"))?  
            .workspace;

        // Emit focus-loss audit entries for all currently focused surfaces.
        let losing: Vec<u64> = state
            .surfaces
            .values()
            .filter(|s| s.focused)
            .map(|s| s.id)
            .collect();
        for lid in losing {
            state.record_focus_event(lid, false);
            if let Some(s) = state.surfaces.get_mut(&lid) {
                s.focused = false;
            }
        }

        // Grant focus and emit audit entry.
        if let Some(surface) = state.surfaces.get_mut(&surface_id) {
            surface.focused = true;
        }
        state.record_focus_event(surface_id, true);
        state.active_workspace = workspace;
        state.workspace_focus.insert(workspace, Some(surface_id));
        Ok(())
    }

    /// Returns `true` if normal application surfaces may be presented.
    ///
    /// Normal surface presentation is blocked when any Critical overlay
    /// is visible (DSK-005: safety overlays preempt ordinary app chrome).
    pub fn can_present_normal_surface(state: &DesktopState) -> bool {
        !state.overlays.iter().any(|overlay| {
            overlay.visible && matches!(overlay.priority, OverlayPriority::Critical)
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::state::DesktopState;

    #[test]
    fn register_and_focus_records_audit() {
        let mut state = DesktopState::default();
        let mut compositor = CompositorFacade::default();

        let id = compositor.register_surface(&mut state, "org.gaia.test", "Test", 0, false);
        compositor.focus_surface(&mut state, id).unwrap();

        assert!(state.surfaces[&id].focused);
        assert_eq!(state.workspace_focus[&0], Some(id));
        // One focus-gain audit entry expected.
        assert!(state.focus_audit_log.iter().any(|(sid, gained, _)| *sid == id && *gained));
    }

    #[test]
    fn critical_overlay_blocks_normal_surface() {
        use crate::state::{OverlayPriority, OverlayRecord};
        let mut state = DesktopState::default();
        state.overlays.push(OverlayRecord {
            id: 1, label: "GUARDIAN".into(),
            priority: OverlayPriority::Critical, visible: true,
        });
        assert!(!CompositorFacade::can_present_normal_surface(&state));
    }

    #[test]
    fn info_overlay_does_not_block() {
        use crate::state::{OverlayPriority, OverlayRecord};
        let mut state = DesktopState::default();
        state.overlays.push(OverlayRecord {
            id: 2, label: "status".into(),
            priority: OverlayPriority::Info, visible: true,
        });
        assert!(CompositorFacade::can_present_normal_surface(&state));
    }
}
