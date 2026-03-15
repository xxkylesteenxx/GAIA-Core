//! Window manager — tiling layout and overlay upsert.
//!
//! Owns:
//!   - `switch_workspace`  — activate a workspace
//!   - `tile_layout`       — compute tiled surface geometry (returns Vec<(u64, Rect)>)
//!   - `upsert_overlay`    — insert or update a named overlay; maintains
//!                           priority-sorted overlay order for HUD / z-band rendering
//!
//! `Rect` is the canonical 2-D axis-aligned rectangle used throughout
//! the desktop runtime for surface geometry.
//!
//! Layout constants (width=1000, height=700) are scaffold values.
//! Replace with real output geometry from `DesktopConfig::outputs` once
//! the Smithay backend is wired.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.2

use crate::state::{DesktopState, GaiaCore, OverlayPriority, OverlayRecord, SurfaceRecord};

/// Axis-aligned rectangle in logical pixels.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Rect {
    pub x:      i32,
    pub y:      i32,
    pub width:  i32,
    pub height: i32,
}

/// Window manager — stateless helpers over `DesktopState`.
pub struct WindowManager;

impl WindowManager {
    /// Activate a workspace by index.
    pub fn switch_workspace(state: &mut DesktopState, workspace: usize) {
        state.active_workspace = workspace;
    }

    /// Compute tiled layout for a workspace.
    ///
    /// Returns `(surface_id, Rect)` pairs sorted by surface id.
    /// Floating surfaces are excluded — they are positioned by the compositor.
    ///
    /// Layout strategy: single row, equal-width columns.
    /// Scaffold dimensions: 1000×700 logical pixels.
    /// Replace with `config.outputs[n].logical_width/height()` in production.
    pub fn tile_layout(state: &DesktopState, workspace: usize) -> Vec<(u64, Rect)> {
        let mut surfaces: Vec<&SurfaceRecord> = state
            .surfaces
            .values()
            .filter(|s| s.workspace == workspace && !s.floating)
            .collect();
        surfaces.sort_by_key(|s| s.id);

        if surfaces.is_empty() {
            return Vec::new();
        }

        let width      = 1000_i32;
        let height     = 700_i32;
        let count      = surfaces.len() as i32;
        let each_width = width / count.max(1);

        surfaces
            .into_iter()
            .enumerate()
            .map(|(idx, s)| {
                (
                    s.id,
                    Rect {
                        x:      idx as i32 * each_width,
                        y:      0,
                        width:  each_width,
                        height,
                    },
                )
            })
            .collect()
    }

    /// Insert or update an overlay by string id.
    ///
    /// After every mutation the overlay list is sorted by ascending priority
    /// (Normal → Warning → Critical) so the HUD and z-band renderer always
    /// encounter overlays in escalation order without a separate sort step.
    ///
    /// Only trusted runtime code may call this function (DSK-009).
    pub fn upsert_overlay(
        state:    &mut DesktopState,
        id:       impl Into<String>,
        owner:    GaiaCore,
        priority: OverlayPriority,
        visible:  bool,
        message:  impl Into<String>,
    ) {
        let id = id.into();

        match state.overlays.iter_mut().find(|o| o.id == id) {
            Some(existing) => {
                existing.owner    = owner;
                existing.priority = priority;
                existing.visible  = visible;
                existing.message  = message.into();
            }
            None => state.overlays.push(OverlayRecord {
                id, owner, priority, visible, message: message.into(),
            }),
        }

        // Maintain priority-sorted order: Normal < Warning < Critical.
        state.overlays.sort_by_key(|o| match o.priority {
            OverlayPriority::Normal   => 0_u8,
            OverlayPriority::Warning  => 1,
            OverlayPriority::Critical => 2,
        });
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{compositor::CompositorFacade, state::DesktopState};

    fn two_surface_state() -> (DesktopState, u64, u64) {
        let mut state = DesktopState::default();
        let mut c = CompositorFacade::default();
        let tiled    = c.register_surface(&mut state, "app", "App", 0, false);
        let floating = c.register_surface(&mut state, "hud", "HUD", 0, true);
        (state, tiled, floating)
    }

    #[test]
    fn tile_layout_excludes_floating() {
        let (state, tiled, _) = two_surface_state();
        let layout = WindowManager::tile_layout(&state, 0);
        assert_eq!(layout.len(), 1);
        assert_eq!(layout[0].0, tiled);
    }

    #[test]
    fn tile_layout_single_surface_fills_width() {
        let (state, tiled, _) = two_surface_state();
        let layout = WindowManager::tile_layout(&state, 0);
        let rect = layout[0].1;
        assert_eq!(rect, Rect { x: 0, y: 0, width: 1000, height: 700 });
        let _ = tiled;
    }

    #[test]
    fn tile_layout_two_tiled_splits_evenly() {
        let mut state = DesktopState::default();
        let mut c = CompositorFacade::default();
        let a = c.register_surface(&mut state, "a", "A", 0, false);
        let b = c.register_surface(&mut state, "b", "B", 0, false);
        let layout = WindowManager::tile_layout(&state, 0);
        assert_eq!(layout.len(), 2);
        assert_eq!(layout[0], (a, Rect { x: 0,   y: 0, width: 500, height: 700 }));
        assert_eq!(layout[1], (b, Rect { x: 500, y: 0, width: 500, height: 700 }));
    }

    #[test]
    fn upsert_maintains_priority_order() {
        let mut state = DesktopState::default();
        WindowManager::upsert_overlay(
            &mut state, "w", GaiaCore::Terra, OverlayPriority::Warning, true, "warn",
        );
        WindowManager::upsert_overlay(
            &mut state, "n", GaiaCore::Sophia, OverlayPriority::Normal, true, "normal",
        );
        WindowManager::upsert_overlay(
            &mut state, "c", GaiaCore::Guardian, OverlayPriority::Critical, true, "crit",
        );
        // Should be sorted: Normal, Warning, Critical
        assert_eq!(state.overlays[0].priority, OverlayPriority::Normal);
        assert_eq!(state.overlays[1].priority, OverlayPriority::Warning);
        assert_eq!(state.overlays[2].priority, OverlayPriority::Critical);
    }

    #[test]
    fn upsert_escalation_re_sorts() {
        let mut state = DesktopState::default();
        WindowManager::upsert_overlay(
            &mut state, "g", GaiaCore::Guardian, OverlayPriority::Warning, true, "initial",
        );
        WindowManager::upsert_overlay(
            &mut state, "t", GaiaCore::Terra, OverlayPriority::Normal, true, "normal",
        );
        // Escalate g to Critical — it should move to end.
        WindowManager::upsert_overlay(
            &mut state, "g", GaiaCore::Guardian, OverlayPriority::Critical, true, "escalated",
        );
        assert_eq!(state.overlays.last().unwrap().id, "g");
        assert_eq!(state.overlays.last().unwrap().priority, OverlayPriority::Critical);
    }
}
