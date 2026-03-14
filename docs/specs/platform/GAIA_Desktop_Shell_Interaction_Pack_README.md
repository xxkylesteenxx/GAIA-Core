# GAIA Desktop Shell Interaction Pack

**Spec ref:** [GAIA Desktop Shell and Interaction Substrate Spec v1.0](./GAIA_Desktop_Shell_Interaction_Substrate_Spec_v1.0.md)  
**Status:** Starter scaffold — not production-deployed  
**Domain:** `platform/desktop`

---

This pack provides a starter architecture for the GAIA desktop and operator experience. It is the reference implementation scaffold for the normative requirements in the Desktop Shell and Interaction Substrate Spec v1.0.

## Why this split

The compositor should own trusted display, input, and surface policy. The shell should own user experience. This separation keeps rendering and input integrity in Rust while allowing rapid UI iteration in TypeScript.

- The **Rust runtime** enforces the trusted boundary (DSK-001): surface lifecycle, seat/input routing, workspace policy, overlay z-band enforcement, and focus auditability. These concerns are safety-critical and must not be delegated to the TypeScript shell.
- The **TypeScript shell** is explicitly replaceable (DSK-002): operator organisations may substitute an alternative shell implementation without modifying the Rust runtime, as long as the IPC contract is respected.

## Included

```
docs/specs/platform/
  GAIA_Desktop_Shell_Interaction_Substrate_Spec_v1.0.md   ← normative spec
  GAIA_Desktop_Shell_Interaction_Pack_README.md           ← this file

src/rust/gaia_desktop/
  rust_desktop_runtime/                                   ← Rust compositor/WM scaffold
    src/
      compositor.rs    — surface lifecycle + focus audit
      workspace.rs     — workspace state machine + overlay routing
      overlay.rs       — z-band enforcement + safety overlay policy
      ipc.rs           — IPC server (shell ↔ runtime bridge)
      lib.rs           — crate entry point
    Cargo.toml

src/typescript/ui_shell/
  ui_shell/                                               ← React/TS shell scaffold
    src/
      shell/
        Panel.tsx           — top-level operator panel
        LaunchSurface.tsx   — application launch surface
        WorkspaceSwitcher.tsx
      hud/
        ConsciousnessHUD.tsx   — real-time status + alert escalation
        AlertBanner.tsx        — informational / warning / blocking states
      accessibility/
        A11yProvider.tsx       — preference persistence + live regions
        KeyboardNav.tsx        — keyboard traversal + focus restoration
      ipc/
        RuntimeClient.ts       — IPC client (runtime ↔ shell bridge)
    package.json
    tsconfig.json
```

## Validation status

| Component | Status |
|---|---|
| Rust scaffold | Validated locally with `cargo check` |
| TypeScript shell | Source scaffold provided; not dependency-built in this sandbox |
| Spec compliance | Requirements DSK-001–010 traced to scaffold modules |
| Accessibility | `@axe-core/react` wired in CI; audit pending |

## Integration direction

1. **Rust runtime** — replace facade modules with [Smithay](https://github.com/Smithay/smithay)-based Wayland protocol handling and backend integration. Keep workspace policy, overlay enforcement, and HUD bridging as separate Rust services.
2. **IPC layer** — harden `ipc.rs` / `RuntimeClient.ts` for the production message contract. Consider using a Unix domain socket with credential-based authentication so the shell cannot impersonate the compositor.
3. **React shell** — treat as the primary operator-facing surface. Add strong accessibility defaults (ARIA landmarks, live regions, keyboard traversal) from the first component. Wire `A11yProvider.tsx` at the root and do not ship panels that have not passed `axe` clean.
4. **HUD** — implement the three-state alert taxonomy (informational / warning / blocking) per §6.2 of the spec before wiring live planetary state. Blocking alerts require explicit operator dismissal — do not allow automated agent dismissal.
5. **Safety overlays** — implement overlay z-band enforcement in `overlay.rs` before connecting any untrusted application surface. This is a hard security requirement (DSK-009).

## See also

- [GAIA Desktop Shell and Interaction Substrate Spec v1.0](./GAIA_Desktop_Shell_Interaction_Substrate_Spec_v1.0.md)
- [VIRT-MEM-IPC-SPEC v1.0](../VIRT-MEM-IPC-SPEC-v1.0.md)
- [GAIA Inter-Process Communication Spec v1.0](../GAIA_Inter_Process_Communication_Spec_v1.0.md)
- [GAIA Linux Kernel Modifications Spec v1.0](../GAIA_Linux_Kernel_Modifications_Spec_v1.0.md)
