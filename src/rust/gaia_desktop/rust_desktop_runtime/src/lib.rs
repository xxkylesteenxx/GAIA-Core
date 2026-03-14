//! GAIA Desktop Runtime crate entry point.
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0
//! docs/specs/platform/GAIA_Desktop_Shell_Interaction_Substrate_Spec_v1.0.md
//!
//! Module layout
//! -------------
//! state       — shared DesktopState, SurfaceRecord, OverlayRecord, OverlayPriority
//! compositor  — surface lifecycle + focus auditability          (DSK-008)
//! workspace   — workspace state machine + overlay routing        (DSK-005)
//! overlay     — z-band enforcement + safety overlay policy       (DSK-009)
//! ipc         — Unix socket IPC server scaffold (shell ↔ runtime)
//!
//! All modules within this crate remain inside the trusted runtime
//! boundary (DSK-001). The TypeScript shell communicates exclusively
//! through the IPC layer — no direct FFI or shared memory.

pub mod compositor;
pub mod ipc;
pub mod overlay;
pub mod state;
pub mod workspace;

pub use state::{DesktopState, OverlayPriority, OverlayRecord, SurfaceRecord};
