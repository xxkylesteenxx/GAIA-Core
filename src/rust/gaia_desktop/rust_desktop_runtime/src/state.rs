//! Shared desktop state types.
//!
//! DesktopState is the single source of truth for the compositor,
//! window manager, and overlay subsystems. All mutations go through
//! the facade modules (compositor, workspace, overlay) — state is
//! never mutated directly by the IPC layer.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2

use std::collections::HashMap;

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

/// Priority tier for overlay surfaces.
///
/// Critical overlays preempt all application chrome (DSK-005).
/// Safety overlays are non-spoofable by untrusted applications (DSK-009).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum OverlayPriority {
    /// Informational — blue tone, non-blocking, auto-dismisses after TTL.
    Info,
    /// Warning — amber tone, non-blocking, persists until acknowledged.
    Warning,
    /// Critical / blocking — red tone, modal, requires explicit operator action.
    /// Preempts all normal application chrome.
    Critical,
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
