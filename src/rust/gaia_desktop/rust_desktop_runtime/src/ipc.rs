//! IPC server scaffold — shell ↔ runtime bridge.
//!
//! Provides the typed message contract between the TypeScript shell
//! and the trusted Rust runtime. In production, this module should
//! bind a Unix domain socket with credential-based authentication
//! so the shell cannot impersonate the compositor.
//!
//! Scaffold: message types are defined and serialisation stubs are
//! provided. Replace stub dispatch with real async socket handling
//! (e.g. tokio + serde_json) when the IPC contract is stabilised.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2, §6.2
//! Cross-ref: VIRT-MEM-IPC-SPEC v1.0

/// Messages the TypeScript shell sends to the runtime.
///
/// Expand as the shell ↔ runtime protocol is stabilised.
#[derive(Debug)]
pub enum ShellToRuntime {
    /// Request focus for a surface by id.
    FocusSurface { surface_id: u64 },
    /// Request workspace switch.
    SwitchWorkspace { target: usize },
    /// Operator confirms dismissal of a blocking overlay.
    DismissOverlay { overlay_id: u64 },
    /// Shell is ready to receive HUD state updates.
    SubscribeHud,
}

/// Messages the runtime sends to the TypeScript shell.
///
/// Expand as the shell ↔ runtime protocol is stabilised.
#[derive(Debug)]
pub enum RuntimeToShell {
    /// Current focused surface changed.
    FocusChanged { surface_id: Option<u64> },
    /// Active workspace changed.
    WorkspaceChanged { workspace: usize },
    /// Overlay visibility changed (id, visible).
    OverlayUpdate { overlay_id: u64, visible: bool },
    /// Full HUD state snapshot (sent on SubscribeHud and on state change).
    HudSnapshot(HudState),
    /// A critical alert requires operator action.
    CriticalAlert { overlay_id: u64, label: String },
}

/// HUD state snapshot sent to the shell on subscription and on change.
#[derive(Debug, Default)]
pub struct HudState {
    pub active_workspace:  usize,
    pub focused_surface:   Option<u64>,
    pub critical_overlays: Vec<u64>,
    pub warning_overlays:  Vec<u64>,
}

/// IPC server scaffold.
///
/// In production, replace the dispatch stub with a tokio async task
/// reading framed JSON messages from a Unix domain socket.
pub struct IpcServer;

impl IpcServer {
    /// Dispatch a shell message against the provided mutable state.
    ///
    /// Returns a list of outbound messages to send back to the shell.
    /// Scaffold: all paths return stubs. Wire real compositor/overlay/
    /// workspace calls here once the async socket layer is in place.
    pub fn dispatch(
        &self,
        msg: ShellToRuntime,
        state: &mut crate::state::DesktopState,
    ) -> Vec<RuntimeToShell> {
        match msg {
            ShellToRuntime::FocusSurface { surface_id } => {
                // TODO: call CompositorFacade::focus_surface
                let _ = (surface_id, &mut *state);
                vec![RuntimeToShell::FocusChanged { surface_id: Some(surface_id) }]
            }
            ShellToRuntime::SwitchWorkspace { target } => {
                state.active_workspace = target;
                vec![RuntimeToShell::WorkspaceChanged { workspace: target }]
            }
            ShellToRuntime::DismissOverlay { overlay_id } => {
                // TODO: call OverlayManager::dismiss_overlay with operator_confirmed=true
                vec![RuntimeToShell::OverlayUpdate { overlay_id, visible: false }]
            }
            ShellToRuntime::SubscribeHud => {
                let snapshot = HudState {
                    active_workspace: state.active_workspace,
                    focused_surface: state
                        .workspace_focus
                        .get(&state.active_workspace)
                        .copied()
                        .flatten(),
                    critical_overlays: state
                        .overlays
                        .iter()
                        .filter(|o| o.visible && matches!(o.priority, crate::state::OverlayPriority::Critical))
                        .map(|o| o.id)
                        .collect(),
                    warning_overlays: state
                        .overlays
                        .iter()
                        .filter(|o| o.visible && matches!(o.priority, crate::state::OverlayPriority::Warning))
                        .map(|o| o.id)
                        .collect(),
                };
                vec![RuntimeToShell::HudSnapshot(snapshot)]
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::state::DesktopState;

    #[test]
    fn subscribe_hud_returns_snapshot() {
        let mut state = DesktopState::default();
        let server = IpcServer;
        let responses = server.dispatch(ShellToRuntime::SubscribeHud, &mut state);
        assert!(matches!(responses[0], RuntimeToShell::HudSnapshot(_)));
    }

    #[test]
    fn switch_workspace_updates_state() {
        let mut state = DesktopState::default();
        let server = IpcServer;
        server.dispatch(ShellToRuntime::SwitchWorkspace { target: 2 }, &mut state);
        assert_eq!(state.active_workspace, 2);
    }
}
