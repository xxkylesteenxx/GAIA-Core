# GAIA Language Stack Specification v1.0

**Document ID**: GAIALanguageStackSpecv1.0  
**Status**: Canonical  
**Date**: March 12, 2026  
**Classification**: Technical Specification  
**Scope**: Language and toolchain policy for all GAIA layers (L0–L6)

---

## v1 Boundary Compliance

```
---
v1 Boundary Compliance: IN SCOPE
Relevant v1 Sections: 3, 4, 5, 8, 9, 13
Post-v1 Tag: NO
Post-v1 Milestone: N/A
Scope Matrix Tier: MUST SHIP
---
```

---

## 1. Purpose

This specification defines the canonical language and toolchain policy for every layer of the GAIA operating system stack. It governs which languages are permitted at each layer, why, and what the enforcement rules are. All GAIA repositories, PRs, and implementation plans must comply with this document.

---

## 2. Design Principles

- **Safety first**: Rust for all new kernel/driver/VMM/service code. C only where existing Linux substrate requires it.
- **Polish**: C++ and Rust for graphics/desktop to match macOS/Windows UX quality via Wayland/GCompositor.
- **Velocity**: Python for AI, orchestration, tooling, and research. Multi-language SDK for extensibility.
- **Universality**: No clean-room kernel rewrite. Modify Linux/KVM with Rust where upstream supports it.
- **Layered boundaries**: Strict no-bleed rules. Python and TypeScript are prohibited below Layer 4. C++ is prohibited below Layer 2 except for minimal glue.

---

## 3. Canonical Layer Stack

| Layer | Name | Primary Languages | Key Components |
|-------|------|-------------------|----------------|
| **L0** | Boot / Hardware Entry | Assembly, C (+ Rust later) | UEFI/BIOS stubs, TPM handoff, CPU init, IOMMU setup |
| **L1** | Kernel / Hypervisor Core | Rust (first), C, Assembly stubs | Scheduler (sched_ext), MM, IPC, caps, process model, KVM hooks |
| **L2** | HAL / Drivers | Rust, C (+ C++ rarely) | HAL-1/2 brokers, D2/D3 device drivers, IOMMU policy |
| **L3** | Hypervisor / VMM / Guest | Rust, C (+ C++ optional) | rust-vmm, Cloud Hypervisor, virtio devices, snapshots, guest remoting |
| **L4** | Graphics / Compositor / Desktop Shell | Rust, C++ | GCompositor (Wayland), GShell, GDash, GScene, GBufferManager |
| **L5** | AI / Orchestration / Automation | Python, Rust, TypeScript | llama.cpp/vLLM, Lava/Brian2, Next.js, Jupyter, Helm/Ansible |
| **L6** | Apps / SDK / Scripting / Plugins | Rust, TypeScript, Python, WASM | Wayland-native apps, GAPI SDKs, WASM plugins (wasmtime) |

---

## 4. Per-Layer Language Rules

### L0 — Boot / Hardware Entry
- **Assembly**: CPU boot vectors, context switch glue, early init stubs.
- **C**: UEFI bootloader, firmware interaction, TPM bring-up, ACPI tables.
- **Rust (future)**: New initramfs components and boot-time integrity checks as upstream matures.
- **Prohibited**: Python, TypeScript, C++, WASM.

### L1 — Kernel / Hypervisor Core
- **Rust (first)**: All new subsystems — scheduler plugins (sched_ext/scx), LSM extensions, IPC primitives, capability tables, KVM device hooks, isolation boundaries (seccomp/Landlock).
- **C**: Legacy mm, process model, POSIX baseline, existing scheduler CFS core.
- **Assembly stubs**: vCPU context, CPU topology glue.
- **Prohibited**: C++, Python, TypeScript.

### L2 — HAL / Drivers
- **Rust**: All new HAL layers (HAL-1 kernel HW interfaces, HAL-2 device brokers), new D2/D3 peripheral drivers, IOMMU-safe device policy, sensor drivers.
- **C**: D1 mandatory boot-critical drivers (storage/net/display at boot time), legacy firmware drivers.
- **C++ (rare)**: Only if a vendor HAL or graphics HAL has no viable Rust alternative.
- **Prohibited**: Python, TypeScript.

### L3 — Hypervisor / VMM / Guest Execution
- **Rust**: VMM core (rust-vmm crates), vCPU execution (kvm_ioctls), virtio devices (net/disk/gpu/fs), guest memory (vm-memory), snapshots, suspend/resume, guest-host window remoting (virtio-fs/vhost-user).
- **C**: KVM kernel-side substrate, legacy QEMU compatibility stubs, paravirt drivers.
- **C++ (optional)**: Emulated GPU models (virglrenderer/gfxstream) if unavoidable.
- **Prohibited**: Python, TypeScript.

### L4 — Graphics / Compositor / Desktop Shell
- **Rust**: Wayland-native compositor logic, GCompositor protocol handling, GShell desktop shell extensions, animation engine, buffer policy (GBufferManager), trusted overlay management.
- **C++**: Mesa/Vulkan/OpenGL renderer integration, GDash 3D scene graph, GScene spatial renderer, Xwayland bridge, atomic KMS pipeline wrappers.
- **Prohibited**: Python, WASM in hot paths.

### L5 — AI / Orchestration / Automation
- **Python**: Agent orchestration (llama.cpp, vLLM, JetStream), ML pipelines (Brian2/Lava neuromorphic), tooling (pytest, Jupyter, Poetry), DevOps/packaging (Helm, Ansible, Docker), research, plugins.
- **Rust**: Performance-critical inference wrappers, GAPI service daemons, sched/IPC bridges.
- **TypeScript**: Operator consoles, approval UIs (Next.js), web-based dashboards, SDK surfaces.
- **Prohibited**: Assembly, C, C++ (except vendored inference backends).

### L6 — Apps / SDK / Scripting / Plugins
- **Rust**: Native Wayland apps, system utilities, performance-sensitive platform components.
- **TypeScript**: Web-tech apps (Electron/Chromium), SDK client libraries, portal UIs.
- **Python**: Scripting, automation, plugin authoring, developer tools.
- **WASM**: Sandboxed plugins via wasmtime with seccomp-gated capability grants and plugin manifests.
- **Prohibited**: Direct kernel syscalls (must go through GAPI broker).

---

## 5. Interop and Toolchain

| Concern | Tool |
|---------|------|
| C → Rust FFI | `cbindgen`, `bindgen` |
| Rust → WASM | `wasm-bindgen`, `wasm-pack` |
| C++ → Rust | `cxx` crate |
| Build (Rust) | `cargo`, workspace `Cargo.toml` |
| Build (C/C++) | `CMake`, `Meson` |
| Build (Python) | `Poetry`, `PDM` |
| Build (TS) | `npm`, `pnpm`, `esbuild` |
| Proto/SDK gen | Protobuf → Rust/TS/Python/Go via GAPI |
| Plugin system | JSON manifest + seccomp/WASM capability gates |

---

## 6. Enforcement Rules

- All new GAIA-Core L0–L3 code must be Rust or C. C++ PRs require explicit sign-off with rationale.
- All new GAIA-Desktop L4 code must be Rust or C++. No Python in compositor hot paths.
- Python, TypeScript, and WASM are prohibited below L4 in production paths.
- PR checklist item: **Layer/language compliant? [Y/N]** — required on every PR.
- Metric tracked: Rust % in kernel and driver code. Target: >50% by v1.1, >70% by v2.

---

## 7. Adoption Order (v1)

1. Commit this spec to `docs/specs/platform/` — **immediate**.
2. Add PR checklist enforcement — **immediate**.
3. Scaffold L1 kernel Rust module — **Phase 0**.
4. Scaffold L2 HAL Rust broker — **Phase 0**.
5. Scaffold L3 VMM rust-vmm entry — **Phase 1**.
6. Scaffold L4 GCompositor Wayland stub — **Phase 1**.
7. Wire L5 Python AI orchestration — **Phase 1** (already partially exists).
8. Wire L6 SDK multi-lang generation — **Phase 2**.

---

## 8. References

- `GAIA_Linux_Kernel_Modifications_Spec_v1.0.md`
- `GAIA_Inter_Process_Communication_Spec_v1.0.md`
- `GAIA_Graphics_Subsystem_Specification_v1.0` (canonical volume)
- `GAIA_Canonical_Volume_01_OS_Foundation.md`
- rust-vmm community: https://github.com/rust-vmm
- Rusty Linux (2024): https://arxiv.org/pdf/2407.18431v2.pdf
- Cloud Hypervisor guide (2026): https://northflank.com/blog/guide-to-cloud-hypervisor
