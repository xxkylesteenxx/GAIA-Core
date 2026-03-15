//! GAIA Desktop Runtime — library entry point.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0

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
pub use state::{
    DesktopState, GaiaCore, OverlayPriority, OverlayRecord, SurfaceRecord,
};
// TileSlot removed — tile_layout now returns Vec<(u64, Rect)>.
pub use window_manager::{Rect, WindowManager};
