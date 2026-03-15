//! Shared desktop state types.
//!
//! DesktopState is the single source of truth for the compositor,
//! window manager, and overlay subsystems. All mutations go through
//! the facade modules (compositor, workspace, overlay) — state is
//! never mutated directly by the IPC layer.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2

use std::collections::HashMap;

/// GAIA cognitive / operational cores surfaced in the Consciousness HUD.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum GaiaCore {
    Sophia,
    Guardian,
    Terra,
    Atlas,
    Hermes,
    Mnemosyne,
}

impl GaiaCore {
    pub fn display_name(&self) -> &'static str {
        match self {
            GaiaCore::Sophia    => "SOPHIA",
            GaiaCore::Guardian  => "GUARDIAN",
            GaiaCore::Terra     => "TERRA",
            GaiaCore::Atlas     => "ATLAS",
            GaiaCore::Hermes    => "HERMES",
            GaiaCore::Mnemosyne => "MNEMOSYNE",
        }
    }
}

/// Priority tier for overlay surfaces and HUD core status indicators.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum OverlayPriority {
    Normal,
    Info,
    Warning,
    Critical,
}

impl OverlayPriority {
    pub fn requires_acknowledgement(&self) -> bool {
        matches!(self, OverlayPriority::Critical)
    }
    pub fn blocks_presentation(&self) -> bool {
        matches!(self, OverlayPriority::Critical)
    }
}

/// A registered Wayland surface.
#[derive(Debug, Clone)]
pub struct SurfaceRecord {
    pub id:        u64,
    pub app_id:    String,
    pub title:     String,
    pub workspace: usize,
    pub focused:   bool,
    pub floating:  bool,
}

/// An active overlay surface record.
#[derive(Debug, Clone)]
pub struct OverlayRecord {
    pub id:       u64,
    pub label:    String,
    pub priority: OverlayPriority,
    pub visible:  bool,
    /// Optional GAIA core this overlay belongs to.
    pub core:     Option<GaiaCore>,
}

/// Top-level shared desktop state.
#[derive(Debug, Default)]
pub struct DesktopState {
    pub surfaces:         HashMap<u64, SurfaceRecord>,
    pub workspace_focus:  HashMap<usize, Option<u64>>,
    pub active_workspace: usize,
    pub overlays:         Vec<OverlayRecord>,
    pub focus_audit_log:  Vec<(u64, bool, u64)>,
    pub audit_seq:        u64,
}

impl DesktopState {
    /// Pre-allocate workspace focus slots for `count` workspaces (0-indexed).
    pub fn reserve_workspaces(&mut self, count: usize) {
        for i in 0..count {
            self.workspace_focus.entry(i).or_insert(None);
        }
    }

    /// Append an immutable focus-change audit entry (DSK-008).
    pub fn record_focus_event(&mut self, surface_id: u64, gained: bool) {
        self.audit_seq += 1;
        self.focus_audit_log.push((surface_id, gained, self.audit_seq));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn reserve_workspaces_creates_slots() {
        let mut state = DesktopState::default();
        state.reserve_workspaces(6);
        assert_eq!(state.workspace_focus.len(), 6);
        for i in 0..6 {
            assert_eq!(state.workspace_focus[&i], None);
        }
    }

    #[test]
    fn critical_requires_acknowledgement() {
        assert!(OverlayPriority::Critical.requires_acknowledgement());
        assert!(!OverlayPriority::Warning.requires_acknowledgement());
        assert!(!OverlayPriority::Normal.requires_acknowledgement());
    }

    #[test]
    fn only_critical_blocks_presentation() {
        assert!(OverlayPriority::Critical.blocks_presentation());
        assert!(!OverlayPriority::Warning.blocks_presentation());
        assert!(!OverlayPriority::Info.blocks_presentation());
        assert!(!OverlayPriority::Normal.blocks_presentation());
    }

    #[test]
    fn gaia_core_display_names() {
        assert_eq!(GaiaCore::Sophia.display_name(),   "SOPHIA");
        assert_eq!(GaiaCore::Guardian.display_name(), "GUARDIAN");
        assert_eq!(GaiaCore::Terra.display_name(),    "TERRA");
    }
}
