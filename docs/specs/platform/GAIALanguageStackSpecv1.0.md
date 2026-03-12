# GAIA Language Stack Specification v1.0

**Document ID**: GAIALanguageStackSpecv1.0  
**Status**: Canonical  
**Date**: March 12, 2026  
**Classification**: Technical Specification  
**Scope**: Programming language selection, layer boundaries, and adoption rules for all GAIA repositories

---

## 1. Purpose

This specification defines the canonical programming language stack for GAIA OS across all layers (L0–L6), all device targets (Core, Desktop, Laptop, Server, IoT, Meta), and all subsystems. It governs language selection in all GAIA repos and must be referenced in PR checklists, architecture reviews, and contributor guidelines.

---

## 2. Design Principles

1. **Safety first** — Rust for all new kernel, driver, VMM, and service code. C only where Linux legacy demands it.
2. **Polish** — C++/Rust for compositor, graphics, and shell to match macOS/Windows UX quality via Wayland/GCompositor.
3. **Velocity** — Python for AI, orchestration, tools, and experimentation. TypeScript for web surfaces.
4. **Universality** — No clean-room kernel rewrite. Modify Linux/KVM with Rust where upstream supports it.
5. **Layered boundaries** — No language bleed across layer boundaries (e.g., no Python/TS below L4, no C++ below L2 except glue).
6. **Interop discipline** — Use cbindgen/FFI for C↔Rust, wasm-bindgen for WASM plugins, Protobuf for cross-lang SDK generation.

---

## 3. Canonical Layer Stack

| Layer | Name | Primary Languages | Key Components |
|-------|------|-------------------|----------------|
| **L0** | Boot / Hardware Entry | Assembly, C (+ Rust later) | UEFI/TPM stubs, CPU/IOMMU init, bootloader |
| **L1** | Kernel / Hypervisor Core | Rust (first), C, Assembly | Scheduler (sched_ext), MM, IPC, capabilities, KVM hooks |
| **L2** | HAL / Drivers | Rust, C (+ C++ rare) | HAL-0/1/2, D1/D2/D3 driver classes, IOMMU broker |
| **L3** | Hypervisor / VMM / Guest | Rust, C (+ C++ opt) | rust-vmm, Cloud Hypervisor, virtio devices, snapshots |
| **L4** | Graphics / Compositor / Shell | Rust, C++ | GCompositor, GShell, GDash, GScene, animation engine |
| **L5** | AI / Orchestration / Automation | Python, Rust, TypeScript | vLLM, llama.cpp, Lava, Next.js consoles, pipelines |
| **L6** | Apps / SDK / Scripting | Rust, TypeScript, Python, WASM | Wayland-native apps, SDKs, plugins, WASM sandbox |

---

## 4. Per-Layer Detail

### L0 — Boot / Hardware Entry
- **Assembly**: CPU context vectors, early boot stubs, UEFI entry, interrupt routing.
- **C**: Bootloader (GRUB/EDK2 stubs), early kernel init, firmware interfacing, minimal D1 driver stubs.
- **Rust (future)**: New boot integrity checks, measured boot attestation once upstream stable.
- **Prohibited**: Python, TypeScript, C++ at this layer.

### L1 — Kernel / Hypervisor Core
- **Rust (first)**: Scheduler extensions (sched_ext/scx), new IPC primitives, capability/security (LSM), KVM virt hooks, isolation boundaries (seccomp, Landlock, namespaces).
- **C (second)**: Core MM (vm_area_struct, page tables), process model (POSIX), legacy scheduler baseline, existing IPC (futex, socket).
- **Assembly (stubs)**: CPU topology detection, context switch glue, early init.
- **Prohibited**: C++, Python, TypeScript at this layer.
- **CCO/ICO scheduling classes**: All scheduler code must respect GAIA latency budgets (CCO ≤1ms, ICO ≤10ms).

### L2 — HAL / Drivers
- **Rust (first)**: All new drivers (D2/D3), HAL-1 kernel HW interfaces, HAL-2 device brokers, IOMMU policy gates, peripheral drivers.
- **C (second)**: D1 mandatory drivers (boot-critical storage, network, display), firmware stubs.
- **C++ (rare)**: Only where vendor graphics HAL or perf-critical driver glue demands it.
- **Driver classes**: D1 (mandatory kernel), D2 (GAIA-brokered), D3 (VM-isolated/sandboxed).

### L3 — Hypervisor / VMM / Guest Execution
- **Rust (first)**: Guest CPU (kvm-ioctls), vCPU execution, VMM (rust-vmm/Cloud Hypervisor), virtio devices (net/disk/gpu), snapshots, suspend/resume, guest-host remoting (vhost-user, virtio-fs).
- **C**: KVM kernel substrate, legacy QEMU compatibility stubs, paravirt drivers.
- **C++ (optional)**: Complex emulated device models (virglrenderer, gfxstream for GPU).

### L4 — Graphics / Compositor / Desktop Shell
- **Rust**: Wayland-native apps, GShell extensions, safe compositor logic, input handling, GDash bindings.
- **C++**: GCompositor (Wayland compositor), GScene (scene graph), animation engine, Vulkan/Mesa integration, dma-buf/KMS pipelines.
- **Shared**: GBufferManager (policy/residency), trusted overlay enforcement, Xwayland lifecycle.
- **Performance targets**: 60 FPS baseline, 120 FPS premium hardware, 16.6ms present-to-scanout.

### L5 — AI / Orchestration / Automation
- **Python (first)**: Agent orchestration (vLLM, llama.cpp, LangChain), ML pipelines (Brian2, Lava), Jupyter research, pytest, Helm/Ansible DevOps, packaging.
- **Rust**: Performance-critical inference paths, high-throughput data pipelines, sched-aware workers.
- **TypeScript**: Operator consoles (Next.js), approval UIs, web-tech dashboards, WebGPU sandboxed views.

### L6 — Apps / SDK / Scripting
- **Rust**: Native Wayland apps, high-performance services, safe plugin hosts (wasmtime).
- **TypeScript**: SDK client bindings, Electron/Chromium apps, web-native GAIA interfaces.
- **Python**: Scripting, automation plugins, developer tools, AI-assisted tooling.
- **WASM**: Sandboxed plugins via wasmtime, seccomp-gated, manifest-driven permissions.

---

## 5. Toolchain Summary

| Language | Build Tool | Package Manager | Notes |
|----------|-----------|-----------------|-------|
| Rust | Cargo | crates.io | Workspace Cargo.toml at GAIA-Core root |
| C | Makefile/Kbuild | n/a | Linux kernel conventions |
| C++ | CMake | vcpkg / system | Graphics/compositor only |
| Python | Poetry / PDM | PyPI | AI/tools/orchestration |
| TypeScript | tsc / Vite | npm / pnpm | SDK and web surfaces |
| WASM | wasm-pack | crates.io / npm | Plugin sandbox |

---

## 6. Interoperability Rules

- **C ↔ Rust**: Use `cbindgen` to generate C headers from Rust; `bindgen` to generate Rust bindings from C headers.
- **Rust ↔ Python**: Use `PyO3` for native Python extensions in Rust.
- **Rust ↔ WASM**: Use `wasm-bindgen` and `wasmtime` for plugin hosting.
- **SDK generation**: Protobuf/gRPC-first for cross-language (Python/TS/Go/Rust) SDK generation.
- **FFI discipline**: All unsafe FFI must be wrapped in safe Rust abstractions. No raw C pointer exposure in public APIs.

---

## 7. Adoption Rules

1. **New code**: Default to Rust unless graphics/perf forces C++, or tooling/ML forces Python.
2. **Legacy code**: C only. Do not rewrite working C unless it has active CVEs or is being extended.
3. **Prohibited below L4**: Python, TypeScript.
4. **Prohibited below L2**: C++ (except explicit approval).
5. **Rust kernel %**: Track Rust LOC % in kernel/drivers. Target >50% of new subsystem code in Rust by v2.0.
6. **PR checklist**: Every PR must declare its layer and confirm language compliance.

---

## 8. Repository Mapping

| Repo | Layers | Primary Languages |
|------|--------|-------------------|
| GAIA-Core | L0, L1, L2, L3, L4 | Asm, C, Rust, C++ |
| GAIA-Desktop | L4, L5, L6 | Rust, C++, Python, TS |
| GAIA-Laptop | L4, L5, L6 | Rust, C++, Python, TS |
| GAIA-Server | L1, L3, L5 | Rust, C, Python |
| GAIA-IoT | L0, L1, L2 | Asm, C, Rust |
| GAIA-Meta | L5, L6 | Python, TS, Rust |

---

## 9. Enforcement

- This spec is referenced in `CONTRIBUTING.md` for all GAIA repos.
- CI linting checks language/layer compliance per directory.
- Architecture Decision Records (ADRs) must cite this spec when deviating from defaults.
- Deviations require explicit approval from GAIA core maintainers and an ADR entry.

---

*This specification is cross-referenced with: GAIAGraphicsSubsystemSpecificationv1.0, GAIAConcurrencyModelSpecificationv1.0, GAIANetworkStackSpecificationv1.0, GAIA Canonical Volume 01 OS Foundation.*
