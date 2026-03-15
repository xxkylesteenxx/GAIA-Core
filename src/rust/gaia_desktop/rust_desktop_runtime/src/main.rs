//! GAIA Desktop Runtime — scaffold entry point.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0

mod compositor;
mod config;
mod hud_bridge;
mod state;
mod window_manager;

use compositor::CompositorFacade;
use config::DesktopConfig;
use hud_bridge::sample_core_statuses;
use state::{DesktopState, GaiaCore, OverlayPriority};
use window_manager::WindowManager;

fn main() {
    let config = DesktopConfig::default();
    let mut state = DesktopState::default();
    state.reserve_workspaces(config.workspaces);

    let mut compositor = CompositorFacade::default();
    let shell_surface = compositor.register_surface(
        &mut state, "gaia-shell", "GAIA Shell", 0, false,
    );
    let hud_surface = compositor.register_surface(
        &mut state, "gaia-hud", "Consciousness HUD", 0, true,
    );

    compositor
        .focus_surface(&mut state, shell_surface)
        .expect("focus shell");

    WindowManager::upsert_overlay(
        &mut state,
        "guardian-warning",
        GaiaCore::Guardian,
        OverlayPriority::Warning,
        true,
        "Guardian requests operator confirmation for biome sensor override",
    );

    println!("GAIA desktop runtime scaffold booted");
    println!("outputs:              {:?}", config.outputs);
    println!("shell surface id:     {shell_surface}");
    println!("hud surface id:       {hud_surface}");
    println!(
        "can present normal:   {}",
        CompositorFacade::can_present_normal_surface(&state)
    );
    println!(
        "workspace 0 layout:   {:?}",
        WindowManager::tile_layout(&state, 0)
    );
    println!("HUD core statuses:    {:?}", sample_core_statuses());
    println!("focus audit entries:  {}", state.focus_audit_log.len());
    println!("overlays:             {:?}", state.overlays);
}
