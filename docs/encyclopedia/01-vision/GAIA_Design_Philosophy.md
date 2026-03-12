# GAIA Design Philosophy

> **Part I — Vision, Philosophy & Codex**  
> **Status**: Canonical v1.0 · March 12, 2026

---

## Five Core Principles

### 1. Safety First
Rust for all new kernel, driver, VMM, and service code. C only where the existing Linux substrate requires it. No new C++ below Layer 2 except for minimal graphics glue. The goal: eliminate entire classes of memory-safety CVEs at the language level.

### 2. Polish
The desktop experience must match macOS and Windows in perceived quality. GCompositor, GShell, GDash, and GScene are first-class engineering priorities — not afterthoughts. Wayland-native, 120fps-capable, animation-driven, trusted-overlay-enforced.

### 3. Velocity
Python for AI, orchestration, tooling, and research. TypeScript for web-facing dashboards and SDK surfaces. Rust for performance bottlenecks. No language religion — the right tool at the right layer.

### 4. Universality
One codebase, any device. GAIA-Core is the universal substrate. GAIA-Desktop, GAIA-Laptop, GAIA-Server, and GAIA-IoT are distribution overlays, not forks. Every distribution shares the same kernel, HAL, VMM, and consciousness cores.

### 5. Layered Integrity
Strict no-bleed rules between layers. Python never appears in L0–L3. C++ never appears in L0–L1. TypeScript never appears below L4. Layer boundaries are enforced by PR checklist, not convention.

---

## What This Means in Practice

- A new driver is written in Rust unless a vendor HAL mandates C.
- A new AI feature is written in Python unless it is on the critical inference path.
- A new desktop animation is written in Rust (compositor logic) or C++ (renderer).
- A new plugin is sandboxed via WASM + seccomp, not given raw syscall access.
- A new spec is written before code, not after.

---

## The Honesty Doctrine

GAIA does not overclaim. Every spec carries explicit scope-honesty markers:
- `Starter-grade` = real but not production-hardened.
- `Scaffold` = correct structure, TODOs mark integration points.
- `Post-v1` = valid idea, deferred after MVP.
- `Canonical` = required, buildable, no speculation.

---

*→ Next: [Ethical Architecture](./GAIA_Ethical_Architecture.md)*
