//! Compositor facade — surface lifecycle and focus auditability.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.1, §4.1

use crate::state::{DesktopState, OverlayPriority, SurfaceRecord};

pub struct CompositorFacade {
    next_surface_id: u64,
}

impl Default for CompositorFacade {
    fn default() -> Self { Self { next_surface_id: 1 } }
}

impl CompositorFacade {
    pub fn register_surface(
        &mut self,
        state:     &mut DesktopState,
        app_id:    impl Into<String>,
        title:     impl Into<String>,
        workspace: usize,
        floating:  bool,
    ) -> u64 {
        let id = self.next_surface_id;
        self.next_surface_id += 1;
        state.surfaces.insert(id, SurfaceRecord {
            id, app_id: app_id.into(), title: title.into(),
            workspace, focused: false, floating,
        });
        state.workspace_focus.entry(workspace).or_insert(None);
        id
    }

    pub fn destroy_surface(
        &self,
        state:      &mut DesktopState,
        surface_id: u64,
    ) -> Result<(), String> {
        let record = state.surfaces.remove(&surface_id)
            .ok_or_else(|| format!("unknown surface: {surface_id}"))?;
        if record.focused {
            state.record_focus_event(surface_id, false);
            state.workspace_focus.insert(record.workspace, None);
        }
        Ok(())
    }

    pub fn focus_surface(
        &self,
        state:      &mut DesktopState,
        surface_id: u64,
    ) -> Result<(), String> {
        let workspace = state.surfaces.get(&surface_id)
            .ok_or_else(|| format!("unknown surface: {surface_id}"))?
            .workspace;

        let losing: Vec<u64> = state.surfaces.values()
            .filter(|s| s.focused).map(|s| s.id).collect();
        for lid in losing {
            state.record_focus_event(lid, false);
            if let Some(s) = state.surfaces.get_mut(&lid) { s.focused = false; }
        }
        if let Some(s) = state.surfaces.get_mut(&surface_id) { s.focused = true; }
        state.record_focus_event(surface_id, true);
        state.active_workspace = workspace;
        state.workspace_focus.insert(workspace, Some(surface_id));
        Ok(())
    }

    /// Normal surface presentation is blocked while any Critical overlay is visible (DSK-005).
    pub fn can_present_normal_surface(state: &DesktopState) -> bool {
        !state.overlays.iter().any(|o| {
            o.visible && matches!(o.priority, OverlayPriority::Critical)
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::state::{DesktopState, GaiaCore, OverlayPriority, OverlayRecord};

    #[test]
    fn register_and_focus_records_audit() {
        let mut state = DesktopState::default();
        let mut c = CompositorFacade::default();
        let id = c.register_surface(&mut state, "org.gaia.test", "Test", 0, false);
        c.focus_surface(&mut state, id).unwrap();
        assert!(state.surfaces[&id].focused);
        assert!(state.focus_audit_log.iter().any(|(sid, gained, _)| *sid == id && *gained));
    }

    #[test]
    fn critical_overlay_blocks_normal_surface() {
        let mut state = DesktopState::default();
        state.overlays.push(OverlayRecord {
            id: "guard".into(), owner: GaiaCore::Guardian,
            priority: OverlayPriority::Critical, visible: true,
            message: "test".into(),
        });
        assert!(!CompositorFacade::can_present_normal_surface(&state));
    }

    #[test]
    fn warning_overlay_does_not_block() {
        let mut state = DesktopState::default();
        state.overlays.push(OverlayRecord {
            id: "warn".into(), owner: GaiaCore::Terra,
            priority: OverlayPriority::Warning, visible: true,
            message: "test".into(),
        });
        assert!(CompositorFacade::can_present_normal_surface(&state));
    }
}
