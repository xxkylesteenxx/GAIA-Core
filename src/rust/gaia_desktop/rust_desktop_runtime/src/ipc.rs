//! IPC server scaffold — shell ↔ runtime bridge.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2, §6.2
//! Cross-ref: VIRT-MEM-IPC-SPEC v1.0

use crate::state::{DesktopState, OverlayPriority};

#[derive(Debug)]
pub enum ShellToRuntime {
    FocusSurface    { surface_id: u64 },
    SwitchWorkspace { target: usize },
    DismissOverlay  { overlay_id: String },
    SubscribeHud,
}

#[derive(Debug)]
pub enum RuntimeToShell {
    FocusChanged    { surface_id: Option<u64> },
    WorkspaceChanged { workspace: usize },
    OverlayUpdate   { overlay_id: String, visible: bool },
    HudSnapshot(HudState),
    CriticalAlert   { overlay_id: String, message: String },
}

#[derive(Debug, Default)]
pub struct HudState {
    pub active_workspace:  usize,
    pub focused_surface:   Option<u64>,
    pub critical_overlays: Vec<String>,
    pub warning_overlays:  Vec<String>,
}

pub struct IpcServer;

impl IpcServer {
    pub fn dispatch(
        &self,
        msg:   ShellToRuntime,
        state: &mut DesktopState,
    ) -> Vec<RuntimeToShell> {
        match msg {
            ShellToRuntime::FocusSurface { surface_id } => {
                // TODO: call CompositorFacade::focus_surface
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
                    focused_surface:  state.workspace_focus
                        .get(&state.active_workspace).copied().flatten(),
                    critical_overlays: state.overlays.iter()
                        .filter(|o| o.visible && matches!(o.priority, OverlayPriority::Critical))
                        .map(|o| o.id.clone()).collect(),
                    warning_overlays: state.overlays.iter()
                        .filter(|o| o.visible && matches!(o.priority, OverlayPriority::Warning))
                        .map(|o| o.id.clone()).collect(),
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
        let responses = IpcServer.dispatch(ShellToRuntime::SubscribeHud, &mut state);
        assert!(matches!(responses[0], RuntimeToShell::HudSnapshot(_)));
    }

    #[test]
    fn switch_workspace_updates_state() {
        let mut state = DesktopState::default();
        IpcServer.dispatch(ShellToRuntime::SwitchWorkspace { target: 3 }, &mut state);
        assert_eq!(state.active_workspace, 3);
    }
}
