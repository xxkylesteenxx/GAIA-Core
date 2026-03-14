# GAIA Desktop Shell and Interaction Substrate Spec
**Version:** 1.0  
**Status:** Normative  
**Domain:** `platform/desktop`  
**Cross-refs:** VIRT-MEM-IPC-SPEC v1.0 | GAIA-AI-INFERENCE-SPEC v1.0 §6 | GUARDIAN v1.0

---

## 1. Purpose

This document defines the trusted desktop interaction substrate for GAIA. It covers the compositor, window-management policy, user shell, consciousness HUD, and accessibility layer — collectively the **Interaction Substrate**.

The Interaction Substrate is the boundary between GAIA system services and human operators. It is the primary surface through which operators observe planetary state, act on alerts, and invoke GAIA capabilities.

---

## 2. Layering

The Interaction Substrate is divided into four implementation layers. Each layer has a distinct trust boundary and technology contract.

```
┌───────────────────────────────────────────────────────┐
│  Accessibility Layer         TypeScript                │  ← A11y semantics, keyboard, focus, announcements
├───────────────────────────────────────────────────────┤
│  Consciousness HUD           TypeScript                │  ← Real-time status, alert escalation
├───────────────────────────────────────────────────────┤
│  GAIA Shell / UI Shell       TypeScript + React        │  ← Panels, dashboards, workflows, notifications
├───────────────────────────────────────────────────────┤
│  Window Manager Policy Engine   Rust                  │  ← Workspace policy, tiling, z-order, overlay routing
├───────────────────────────────────────────────────────┤
│  Wayland Compositor Runtime      Rust                  │  ← Surface lifecycle, seat/input, output topology
└───────────────────────────────────────────────────────┘
         ▲ Trusted Runtime Boundary
```

### 2.1 Wayland Compositor Runtime (Rust)

Owns surface lifecycle, seat and input routing, output topology, focus handoff, and trusted display composition. Runs within the trusted runtime boundary. All surface creation and destruction events are recorded to the system audit log.

### 2.2 Window Manager Policy Engine (Rust)

Owns workspace policy, tiling and floating behavior, overlay routing, z-order, and consciousness overlay placement. Policy decisions are evaluated as pure functions against a monotonic workspace state machine — no external side effects are permitted during policy evaluation.

### 2.3 GAIA Shell / UI Shell (TypeScript + React)

Owns panels, launch surfaces, dashboards, controls, notifications, and user-facing workflows. Treated as a **replaceable presentation layer** above compositor and policy services — operator organizations may substitute an alternative shell implementation without modifying the Rust runtime.

### 2.4 Consciousness HUD (TypeScript)

Presents real-time status for active cores, planetary state, safety posture, performance metrics, and alert escalation. HUD update propagation is bounded (see §5) and SHALL NOT starve interactive rendering. Distinct visual treatments are required for informational, warning, and blocking alert states.

### 2.5 Accessibility Layer (TypeScript)

Owns assistive semantics, keyboard traversal, focus restoration, reduced-motion behavior, high-contrast handling, text scaling, and live region announcements. Accessibility is a first-class design concern (see §3) and is verified at every release milestone.

---

## 3. Normative Requirements

| ID | Requirement | Layer | Keyword |
|---|---|---|---|
| DSK-001 | The compositor and window manager SHALL remain within the trusted runtime boundary | Compositor, WM | SHALL |
| DSK-002 | The UI shell SHOULD be treated as a replaceable presentation layer above compositor and policy services | Shell | SHOULD |
| DSK-003 | Accessibility SHALL be designed in, not bolted on later | A11y | SHALL |
| DSK-004 | HUD alerts SHALL distinguish informational, warning, and blocking states | HUD | SHALL |
| DSK-005 | Overlay surfaces for safety and system integrity SHALL preempt ordinary application chrome | WM, Compositor | SHALL |
| DSK-006 | HUD update propagation SHALL be bounded and SHALL NOT starve interactive rendering | HUD | SHALL |
| DSK-007 | Accessibility preferences SHALL be persisted and applied at session start | A11y | SHALL |
| DSK-008 | Input focus changes SHALL be auditable | Compositor | SHALL |
| DSK-009 | Safety overlays SHALL be non-spoofable by untrusted applications | Compositor, WM | SHALL |
| DSK-010 | Critical system notifications SHALL be routed through trusted compositor or shell services | Compositor, Shell | SHALL |

---

## 4. Security and Integrity

### 4.1 Focus Auditability

Every input focus change SHALL be emitted as an auditable event to the system event bus. Events include: surface identity, focus direction (gain / lose), timestamp, and seat identifier. Focus audit records are immutable and append-only.

### 4.2 Safety Overlay Non-Spoofability

Safety overlays originate exclusively from the trusted Rust compositor or window manager policy engine. Untrusted application surfaces SHALL NOT be permitted to set z-order above system overlay z-bands. Overlay z-band assignments are enforced at the compositor level and cannot be overridden by Wayland protocol messages from client applications.

### 4.3 Critical Notification Routing

Critical system notifications — including safety posture changes, GUARDIAN escalations, and planetary alert state transitions — SHALL be delivered exclusively through trusted compositor or shell service channels. Untrusted application notification APIs SHALL NOT be used for critical-path alerts.

### 4.4 Accessibility Preference Persistence

Accessibility preferences (high contrast, reduced motion, text scale, keyboard-only mode) SHALL be persisted in secure session storage and applied before the first shell frame is rendered. Preferences SHALL NOT require a session restart to take effect for dynamically adjustable properties.

---

## 5. Verification

| Test | Pass Condition |
|---|---|
| Cold start | Shell and HUD launch without focus traps or accessibility violations |
| Workspace switch | Focus ownership and visibility invariants are preserved across workspace transitions |
| Accessibility audit | Keyboard traversal, ARIA naming, landmark structure, and live region behavior all pass |
| HUD bounded propagation | HUD update cycles complete within the frame budget and do not cause frame drops in interactive surfaces |
| Overlay preemption | Safety overlay surfaces appear above all application chrome within one compositor frame |
| Focus audit log | All focus changes produce immutable audit entries with correct surface identity and timestamp |
| Overlay spoofing | Untrusted application surfaces cannot raise z-order into system overlay z-bands |

---

## 6. Implementation Notes

This spec separates a **compile-valid Rust desktop runtime scaffold** from a **TypeScript/React shell scaffold**:

- The **Rust runtime** models compositor surface lifecycle, seat/input routing, window manager workspace policy, and overlay z-band enforcement. It exposes a stable IPC interface (see VIRT-MEM-IPC-SPEC v1.0) for shell and HUD clients.
- The **TypeScript shell** models operator UX, HUD state rendering, and accessibility behavior. It communicates with the Rust runtime exclusively through the published IPC interface — no direct FFI or shared memory outside the IPC contract.

### 6.1 Technology Contracts

| Layer | Language | Key Dependencies |
|---|---|---|
| Compositor | Rust | `smithay` or custom Wayland compositor crate |
| Window Manager | Rust | Pure policy crate; no Wayland dependency |
| Shell | TypeScript + React | IPC client; no direct system calls |
| HUD | TypeScript | Shell IPC subscription; bounded update loop |
| A11y | TypeScript | ARIA live regions; `@axe-core/react` in CI |

### 6.2 Consciousness HUD Alert States

```
INFORMATIONAL  — blue tone, non-blocking, auto-dismisses after TTL
WARNING        — amber tone, non-blocking, persists until acknowledged
BLOCKING       — red/critical, modal overlay, requires explicit operator action
```

Blocking alerts preempt the active workspace surface via the window manager overlay routing path. Dismissal requires an authenticated operator action; automated dismissal by GAIA agents is not permitted for blocking-class alerts.

---

## 7. Revision History

| Version | Date | Author | Notes |
|---|---|---|---|
| 1.0 | 2026-03-14 | GAIA Core | Initial normative release |
