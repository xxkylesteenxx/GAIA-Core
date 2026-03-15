// GAIA UI Shell — initial shell state.
//
// ShellState is the TypeScript mirror of the Rust runtime's DesktopState
// as received over the IPC layer. It is the source of truth for all
// shell, HUD, and accessibility components.
//
// Spec ref: GAIA Desktop Shell and Interaction Substrate Spec v1.0 §2
// Cross-ref: src/rust/gaia_desktop/rust_desktop_runtime/src/state.rs

export type OverlayPriority = 'Normal' | 'Warning' | 'Critical';

export type GaiaCore =
  | 'Terra' | 'Aqua' | 'Aero' | 'Vita'
  | 'Sophia' | 'Guardian' | 'Nexus' | 'Eta';

export interface OverlayRecord {
  id:       string;
  owner:    GaiaCore;
  priority: OverlayPriority;
  visible:  boolean;
  message:  string;
}

export interface SurfaceRecord {
  id:        number;
  appId:     string;
  title:     string;
  workspace: number;
  focused:   boolean;
  floating:  boolean;
}

export interface ShellState {
  surfaces:        SurfaceRecord[];
  activeWorkspace: number;
  workspaceCount:  number;
  overlays:        OverlayRecord[];
  focusedSurface:  number | null;
}

export const initialShellState: ShellState = {
  surfaces:        [],
  activeWorkspace: 0,
  workspaceCount:  6,
  overlays:        [],
  focusedSurface:  null,
};
