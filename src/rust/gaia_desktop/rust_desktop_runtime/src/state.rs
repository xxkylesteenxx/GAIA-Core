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
///
/// Each variant corresponds to a named GAIA subsystem whose health
/// status is reported via `CoreStatus` in the HUD module.
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
pub enum GaiaCore {
    /// SOPHIA — knowledge synthesis and reasoning core.
    Sophia,
    /// GUARDIAN — safety posture and policy enforcement core.
    Guardian,
    /// TERRA — environmental data ingest and planetary state core.
    Terra,
    /// ATLAS — infrastructure, resource, and deployment core.
    Atlas,
    /// HERMES — inter-process communication and routing core.
    Hermes,
    /// MNEMOSYNE — memory and knowledge indexing core.
    Mnemosyne,
}

impl GaiaCore {
    /// Human-readable display name for the HUD.
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
///
/// Overlay preemption rules (spec §6.2):
///   Normal    — no visual indicator; nominal operation.
///   Info      — blue tone, non-blocking, auto-dismisses after TTL.
///   Warning   — amber tone, non-blocking, persists until acknowledged.
///   Critical  — red tone, modal overlay, requires explicit operator action.
///              Preempts all normal application chrome (DSK-005).
///              Non-spoofable by untrusted applications (DSK-009).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum OverlayPriority {
    /// Normal / nominal — no alert; nominal operation.
    Normal,
    /// Informational — blue tone, non-blocking, auto-dismisses after TTL.
    Info,
    /// Warning — amber tone, non-blocking, persists until acknowledged.
    Warning,
    /// Critical / blocking — red tone, modal, requires explicit operator action.
    Critical,
}

impl OverlayPriority {
    /// Returns true if this priority tier requires operator acknowledgement.
    pub fn requires_acknowledgement(&self) -> bool {
        matches!(self, OverlayPriority::Critical)
    }

    /// Returns true if this priority blocks normal surface presentation.
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
}

/// Top-level shared desktop state.
///
/// Owned by the runtime event loop; passed by mutable reference
/// into facade operations.
#[derive(Debug, Default)]
pub struct DesktopState {
    /// All registered surfaces keyed by surface id.
    pub surfaces: HashMap<u64, SurfaceRecord>,
    /// Currently focused surface per workspace index.
    pub workspace_focus: HashMap<usize, Option<u64>>,
    /// Index of the currently active workspace.
    pub active_workspace: usize,
    /// Active overlay surfaces (safety, HUD, system integrity).
    pub overlays: Vec<OverlayRecord>,
    /// Append-only focus audit log (DSK-008).
    /// Each entry: (surface_id, focused: bool, monotonic event index).
    pub focus_audit_log: Vec<(u64, bool, u64)>,
    /// Monotonic counter for audit log entries.
    pub audit_seq: u64,
}

impl DesktopState {
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
