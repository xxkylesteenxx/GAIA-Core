//! Desktop runtime configuration types.
//!
//! `DesktopConfig` is the top-level configuration for a GAIA desktop
//! session. It is loaded once at startup and passed into the compositor,
//! window manager, and HUD subsystems.
//!
//! `OutputConfig` describes a single Wayland output (monitor).
//!
//! Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2
//!
//! Integration notes
//! -----------------
//! - Add `serde::Deserialize` derives and load from a TOML/JSON config
//!   file when the session manager is wired.
//! - `hud_reserved_top_px` drives the window manager placement policy:
//!   no tiled surface may be positioned within this top band.
//! - `reduced_motion_default` is applied by the accessibility layer at
//!   session start before the first shell frame renders (DSK-007).

/// Configuration for a single Wayland output (monitor / display).
#[derive(Debug, Clone)]
pub struct OutputConfig {
    /// Human-readable output name (matches Wayland output name or DRM connector).
    pub name:   String,
    /// Output width in physical pixels.
    pub width:  u32,
    /// Output height in physical pixels.
    pub height: u32,
    /// Output scale factor (1.0 = no scaling, 2.0 = HiDPI ×2).
    pub scale:  f32,
}

impl OutputConfig {
    /// Logical width after applying the scale factor.
    pub fn logical_width(&self) -> u32 {
        (self.width as f32 / self.scale).round() as u32
    }

    /// Logical height after applying the scale factor.
    pub fn logical_height(&self) -> u32 {
        (self.height as f32 / self.scale).round() as u32
    }
}

/// Top-level desktop session configuration.
#[derive(Debug, Clone)]
pub struct DesktopConfig {
    /// Connected output descriptors.
    pub outputs: Vec<OutputConfig>,
    /// Number of workspaces to create at startup.
    pub workspaces: usize,
    /// Pixels reserved at the top of every output for the Consciousness HUD.
    /// Window manager placement policy SHALL NOT tile surfaces inside this band.
    pub hud_reserved_top_px: u32,
    /// Whether reduced-motion mode is on by default.
    /// Applied by the accessibility layer before the first shell frame (DSK-007).
    pub reduced_motion_default: bool,
}

impl Default for DesktopConfig {
    fn default() -> Self {
        Self {
            outputs: vec![OutputConfig {
                name:   "ATLAS-PRIMARY".to_string(),
                width:  2560,
                height: 1440,
                scale:  1.0,
            }],
            workspaces:              6,
            hud_reserved_top_px:     40,
            reduced_motion_default:  false,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn default_config_is_valid() {
        let cfg = DesktopConfig::default();
        assert_eq!(cfg.workspaces, 6);
        assert_eq!(cfg.hud_reserved_top_px, 40);
        assert!(!cfg.reduced_motion_default);
        assert_eq!(cfg.outputs.len(), 1);
        assert_eq!(cfg.outputs[0].name, "ATLAS-PRIMARY");
    }

    #[test]
    fn logical_dimensions_no_scale() {
        let output = OutputConfig { name: "test".into(), width: 2560, height: 1440, scale: 1.0 };
        assert_eq!(output.logical_width(),  2560);
        assert_eq!(output.logical_height(), 1440);
    }

    #[test]
    fn logical_dimensions_hidpi() {
        let output = OutputConfig { name: "test".into(), width: 3840, height: 2160, scale: 2.0 };
        assert_eq!(output.logical_width(),  1920);
        assert_eq!(output.logical_height(), 1080);
    }

    #[test]
    fn hud_band_is_nonzero() {
        // Ensures the HUD reserved band is configured before any tiling policy runs.
        let cfg = DesktopConfig::default();
        assert!(cfg.hud_reserved_top_px > 0,
            "hud_reserved_top_px must be > 0 to protect the Consciousness HUD band");
    }
}
