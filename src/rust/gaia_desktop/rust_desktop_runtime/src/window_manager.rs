//! Window manager — tiling layout and overlay upsert.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2.2

use crate::state::{DesktopState, GaiaCore, OverlayPriority, OverlayRecord};

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct TileSlot {
    pub surface_id: u64,
    pub col:        usize,
    pub row:        usize,
}

pub struct WindowManager;

impl WindowManager {
    /// Tiled layout for a workspace — floating surfaces excluded.
    pub fn tile_layout(state: &DesktopState, workspace: usize) -> Vec<TileSlot> {
        let mut tiled: Vec<u64> = state.surfaces.values()
            .filter(|s| s.workspace == workspace && !s.floating)
            .map(|s| s.id).collect();
        tiled.sort();
        tiled.into_iter().enumerate()
            .map(|(col, surface_id)| TileSlot { surface_id, col, row: 0 })
            .collect()
    }

    /// Insert or update an overlay by string id.
    pub fn upsert_overlay(
        state:    &mut DesktopState,
        id:       &str,
        owner:    GaiaCore,
        priority: OverlayPriority,
        visible:  bool,
        message:  &str,
    ) {
        if let Some(existing) = state.overlays.iter_mut().find(|o| o.id == id) {
            existing.owner    = owner;
            existing.priority = priority;
            existing.visible  = visible;
            existing.message  = message.to_string();
        } else {
            state.overlays.push(OverlayRecord {
                id:       id.to_string(),
                owner, priority, visible,
                message:  message.to_string(),
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
        let tiled = c.register_surface(&mut state, "app", "App", 0, false);
        c.register_surface(&mut state, "hud", "HUD", 0, true);
        let layout = WindowManager::tile_layout(&state, 0);
        assert_eq!(layout.len(), 1);
        assert_eq!(layout[0].surface_id, tiled);
    }

    #[test]
    fn upsert_inserts_then_updates() {
        let mut state = DesktopState::default();
        WindowManager::upsert_overlay(
            &mut state, "g", GaiaCore::Guardian, OverlayPriority::Warning, true, "initial",
        );
        WindowManager::upsert_overlay(
            &mut state, "g", GaiaCore::Guardian, OverlayPriority::Critical, true, "escalated",
        );
        assert_eq!(state.overlays.len(), 1);
        assert_eq!(state.overlays[0].priority, OverlayPriority::Critical);
        assert_eq!(state.overlays[0].message, "escalated");
    }
}
