//! Shared desktop state types.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2

use std::collections::{BTreeMap, HashMap};

/// GAIA cognitive / operational cores.
///
/// Ordered by `Ord` so they sort consistently in BTreeMap / display.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
pub enum GaiaCore {
    Terra,
    Aqua,
    Aero,
    Vita,
    Sophia,
    Guardian,
    Nexus,
    Eta,
}

impl GaiaCore {
    pub fn display_name(self) -> &'static str {
        match self {
            GaiaCore::Terra    => "TERRA",
            GaiaCore::Aqua     => "AQUA",
            GaiaCore::Aero     => "AERO",
            GaiaCore::Vita     => "VITA",
            GaiaCore::Sophia   => "SOPHIA",
            GaiaCore::Guardian => "GUARDIAN",
            GaiaCore::Nexus    => "NEXUS",
            GaiaCore::Eta      => "ETA",
        }
    }
}

/// Priority tier for overlay surfaces and HUD status indicators.
///
/// Info removed from the canonical surface type — use Normal for
/// non-alerting status and Warning/Critical for operator-visible tiers.
/// The full four-tier taxonomy (Normal/Info/Warning/Critical) is
/// preserved in the HUD presentation layer.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum OverlayPriority {
    /// Nominal operation — no alert indicator.
    Normal,
    /// Operator-visible warning — amber tone, persists until acknowledged.
    Warning,
    /// Blocking alert — red tone, modal, operator action required (DSK-005).
    Critical,
}

impl OverlayPriority {
    pub fn requires_acknowledgement(self) -> bool {
        matches!(self, OverlayPriority::Critical)
    }
    pub fn blocks_presentation(self) -> bool {
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

/// An active overlay record.
///
/// `id` is a stable string key (e.g. "guardian-warning") so overlays
/// can be upserted by name without a separate id counter.
#[derive(Debug, Clone)]
pub struct OverlayRecord {
    /// Stable string identifier — used as upsert key.
    pub id:       String,
    /// The GAIA core that owns this overlay.
    pub owner:    GaiaCore,
    pub priority: OverlayPriority,
    pub visible:  bool,
    /// Human-readable alert message shown in the HUD.
    pub message:  String,
}

/// Top-level shared desktop state.
#[derive(Debug, Default)]
pub struct DesktopState {
    /// All registered surfaces keyed by numeric surface id.
    pub surfaces:         HashMap<u64, SurfaceRecord>,
    /// Focused surface per workspace, ordered by workspace index.
    pub workspace_focus:  BTreeMap<usize, Option<u64>>,
    /// Active overlay records.
    pub overlays:         Vec<OverlayRecord>,
    /// Index of the currently active workspace.
    pub active_workspace: usize,
    /// Append-only focus audit log: (surface_id, gained, seq).
    pub focus_audit_log:  Vec<(u64, bool, u64)>,
    pub audit_seq:        u64,
}

impl DesktopState {
    /// Pre-allocate workspace focus slots for workspaces 0..count.
    pub fn reserve_workspaces(&mut self, count: usize) {
        for idx in 0..count {
            self.workspace_focus.entry(idx).or_insert(None);
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
        for i in 0..6 { assert_eq!(state.workspace_focus[&i], None); }
    }

    #[test]
    fn overlay_priority_semantics() {
        assert!(OverlayPriority::Critical.requires_acknowledgement());
        assert!(!OverlayPriority::Warning.requires_acknowledgement());
        assert!(!OverlayPriority::Normal.requires_acknowledgement());
        assert!(OverlayPriority::Critical.blocks_presentation());
        assert!(!OverlayPriority::Warning.blocks_presentation());
    }

    #[test]
    fn gaia_core_display_names() {
        assert_eq!(GaiaCore::Terra.display_name(),    "TERRA");
        assert_eq!(GaiaCore::Guardian.display_name(), "GUARDIAN");
        assert_eq!(GaiaCore::Sophia.display_name(),   "SOPHIA");
        assert_eq!(GaiaCore::Aqua.display_name(),     "AQUA");
        assert_eq!(GaiaCore::Nexus.display_name(),    "NEXUS");
        assert_eq!(GaiaCore::Eta.display_name(),      "ETA");
    }

    #[test]
    fn gaia_core_is_ordered() {
        // Ord must be stable for BTreeMap keying.
        let mut cores = vec![
            GaiaCore::Sophia, GaiaCore::Terra, GaiaCore::Guardian,
        ];
        cores.sort();
        assert_eq!(cores[0], GaiaCore::Terra);
    }
}
