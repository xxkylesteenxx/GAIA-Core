//! Window manager — tiling layout and overlay upsert.
//!
//! `WindowManager` provides:
//!   - `tile_layout`    — compute tiled surface geometry for a workspace
//!   - `upsert_overlay` — insert or update a named overlay record
//!
//! These are stateless pure functions over `DesktopState` so they
//! can be used from both the runtime event loop and unit tests.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.2

use crate::state::{DesktopState, GaiaCore, OverlayPriority, OverlayRecord};

/// A tile slot: surface id + its zero-indexed column/row position.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TileSlot {
    pub surface_id: u64,
    pub col:        usize,
    pub row:        usize,
}

/// Window manager — stateless helpers over DesktopState.
pub struct WindowManager;

impl WindowManager {
    /// Return tiled surface layout for a workspace as a list of TileSlots.
    ///
    /// Surfaces are sorted by id and laid out left-to-right in a single row.
    /// Floating surfaces are excluded (they are positioned by the compositor).
    pub fn tile_layout(state: &DesktopState, workspace: usize) -> Vec<TileSlot> {
        let mut tiled: Vec<u64> = state
            .surfaces
            .values()
            .filter(|s| s.workspace == workspace && !s.floating)
            .map(|s| s.id)
            .collect();
        tiled.sort();
        tiled
            .into_iter()
            .enumerate()
            .map(|(col, surface_id)| TileSlot { surface_id, col, row: 0 })
            .collect()
    }

    /// Insert or update an overlay record identified by `label`.
    ///
    /// If an overlay with the same label already exists, its priority,
    /// visibility, and core association are updated in place.
    /// Otherwise a new overlay record is appended.
    ///
    /// Only the trusted runtime may call this function — the IPC layer
    /// SHALL NOT expose upsert_overlay to untrusted shell clients (DSK-009).
    pub fn upsert_overlay(
        state:    &mut DesktopState,
        label:    &str,
        core:     GaiaCore,
        priority: OverlayPriority,
        visible:  bool,
        _reason:  &str,
    ) {
        // Monotonically increasing id used only for new overlays.
        let next_id = state.overlays.iter().map(|o| o.id).max().unwrap_or(0) + 1;

        if let Some(existing) = state.overlays.iter_mut().find(|o| o.label == label) {
            existing.priority = priority;
            existing.visible  = visible;
            existing.core     = Some(core);
        } else {
            state.overlays.push(OverlayRecord {
                id:       next_id,
                label:    label.to_string(),
                priority,
                visible,
                core:     Some(core),
            });
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{compositor::CompositorFacade, state::DesktopState};

    #[test]
    fn tile_layout_excludes_floating() {
        let mut state = DesktopState::default();
        let mut c = CompositorFacade::default();
        let tiled    = c.register_surface(&mut state, "app", "App",    0, false);
        let _floating = c.register_surface(&mut state, "hud", "HUD",   0, true);
        let layout = WindowManager::tile_layout(&state, 0);
        assert_eq!(layout.len(), 1);
        assert_eq!(layout[0].surface_id, tiled);
    }

    #[test]
    fn upsert_overlay_inserts_new() {
        let mut state = DesktopState::default();
        WindowManager::upsert_overlay(
            &mut state, "test-overlay", GaiaCore::Guardian,
            OverlayPriority::Warning, true, "test",
        );
        assert_eq!(state.overlays.len(), 1);
        assert_eq!(state.overlays[0].label, "test-overlay");
    }

    #[test]
    fn upsert_overlay_updates_existing() {
        let mut state = DesktopState::default();
        WindowManager::upsert_overlay(
            &mut state, "test-overlay", GaiaCore::Guardian,
            OverlayPriority::Warning, true, "initial",
        );
        WindowManager::upsert_overlay(
            &mut state, "test-overlay", GaiaCore::Guardian,
            OverlayPriority::Critical, true, "escalated",
        );
        // Still only one record.
        assert_eq!(state.overlays.len(), 1);
        assert_eq!(state.overlays[0].priority, OverlayPriority::Critical);
    }
}
