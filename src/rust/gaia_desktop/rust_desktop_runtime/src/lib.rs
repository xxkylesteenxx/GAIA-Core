//! GAIA Desktop Runtime crate entry point.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0
//! docs/specs/platform/GAIA_Desktop_Shell_Interaction_Substrate_Spec_v1.0.md
//!
//! Module layout
//! -------------
//! config          — DesktopConfig, OutputConfig
//! state           — DesktopState, SurfaceRecord, OverlayRecord, GaiaCore, OverlayPriority
//! compositor      — CompositorFacade: surface lifecycle + focus audit (DSK-008)
//! workspace       — WorkspacePolicyEngine: workspace state machine (DSK-005)
//! window_manager  — WindowManager: tile layout + overlay upsert
//! overlay         — OverlayManager: z-band enforcement (DSK-009)
//! hud_bridge      — CoreStatus, sample_core_statuses
//! ipc             — IPC server scaffold (shell ↔ runtime)

pub mod compositor;
pub mod config;
pub mod hud_bridge;
pub mod ipc;
pub mod overlay;
pub mod state;
pub mod window_manager;
pub mod workspace;

pub use config::{DesktopConfig, OutputConfig};
pub use hud_bridge::{CoreStatus, sample_core_statuses};
pub use state::{DesktopState, GaiaCore, OverlayPriority, OverlayRecord, SurfaceRecord};
pub use window_manager::{TileSlot, WindowManager};
