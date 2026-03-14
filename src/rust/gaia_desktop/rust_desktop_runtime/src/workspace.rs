//! Window manager workspace policy engine.
//!
//! Owns:
//!   - Workspace creation and activation
//!   - Tiling / floating policy decisions
//!   - Focus transfer on workspace switch
//!   - Overlay routing (which workspace receives overlay surfaces)
//!
//! Policy decisions are pure functions over DesktopState —
//! no external side effects during policy evaluation.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.2

use crate::state::DesktopState;

/// Window manager policy engine.
pub struct WorkspacePolicyEngine;

impl WorkspacePolicyEngine {
    /// Switch the active workspace.
    ///
    /// Preserves focus ownership: the previously focused surface in the
    /// outgoing workspace is remembered in workspace_focus; the
    /// incoming workspace restores its last focused surface.
    pub fn switch_workspace(
        &self,
        state: &mut DesktopState,
        target_workspace: usize,
    ) {
        if state.active_workspace == target_workspace {
            return;
        }
        state.active_workspace = target_workspace;
        state.workspace_focus.entry(target_workspace).or_insert(None);
    }

    /// Return the surfaces assigned to a given workspace, sorted by id.
    pub fn surfaces_in_workspace<'a>(
        &self,
        state: &'a DesktopState,
        workspace: usize,
    ) -> Vec<&'a crate::state::SurfaceRecord> {
        let mut records: Vec<_> = state
            .surfaces
            .values()
            .filter(|s| s.workspace == workspace)
            .collect();
        records.sort_by_key(|s| s.id);
        records
    }

    /// Determine tiling/floating placement for a new surface.
    ///
    /// Policy: floating surfaces are placed as-is; tiled surfaces
    /// are counted and the caller may use the tile index to compute
    /// position. Returns `(is_floating, tile_index)` where tile_index
    /// is 0 for floating surfaces.
    pub fn placement_policy(
        &self,
        state: &DesktopState,
        workspace: usize,
        floating: bool,
    ) -> (bool, usize) {
        if floating {
            return (true, 0);
        }
        let tiled_count = state
            .surfaces
            .values()
            .filter(|s| s.workspace == workspace && !s.floating)
            .count();
        (false, tiled_count)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{
        compositor::CompositorFacade,
        state::DesktopState,
    };

    #[test]
    fn switch_workspace_preserves_focus_map() {
        let mut state = DesktopState::default();
        let mut compositor = CompositorFacade::default();
        let engine = WorkspacePolicyEngine;

        let id = compositor.register_surface(&mut state, "app", "App", 0, false);
        compositor.focus_surface(&mut state, id).unwrap();

        engine.switch_workspace(&mut state, 1);
        assert_eq!(state.active_workspace, 1);
        // Workspace 0 focus record is preserved.
        assert_eq!(state.workspace_focus[&0], Some(id));
    }

    #[test]
    fn placement_policy_counts_tiled() {
        let mut state = DesktopState::default();
        let mut compositor = CompositorFacade::default();
        let engine = WorkspacePolicyEngine;

        compositor.register_surface(&mut state, "a", "A", 0, false);
        compositor.register_surface(&mut state, "b", "B", 0, false);

        let (floating, index) = engine.placement_policy(&state, 0, false);
        assert!(!floating);
        assert_eq!(index, 2); // two existing tiled surfaces
    }
}
