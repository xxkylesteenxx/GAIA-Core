# GAIA Layer Stack Overview

> **Part II — The GAIA Stack**  
> **Status**: Canonical v1.0 · March 12, 2026

---

## The Seven Engineering Layers (L0–L6)

These are the **implementation layers** — the code layers that make GAIA run.

| Layer | Name | Languages | Key Components |
|-------|------|-----------|----------------|
| **L0** | Boot / Hardware Entry | Asm, C | UEFI/BIOS, TPM, CPU init, IOMMU |
| **L1** | Kernel / Hypervisor Core | Rust, C, Asm | sched_ext, MM, IPC, caps, KVM hooks |
| **L2** | HAL / Drivers | Rust, C | HAL-1/2 brokers, D1–D3 drivers |
| **L3** | Hypervisor / VMM / Guest | Rust, C | rust-vmm, virtio, snapshots, remoting |
| **L4** | Graphics / Desktop Shell | Rust, C++ | GCompositor, GShell, GDash, GScene |
| **L5** | AI / Orchestration | Python, Rust, TS | llama.cpp, Lava, Helm, Next.js |
| **L6** | Apps / SDK / Plugins | Rust, TS, Python, WASM | GAPI SDKs, wasmtime plugins |

→ See full language rules: [Language Stack Spec v1.0](../../specs/platform/GAIA_Language_Stack_Spec_v1.0.md)

---

## The Twelve Canonical Layers (L1–L12)

These are the **architectural layers** from the canonical corpus — broader than the engineering layers and covering the full stack from kernel to planetary coordination.

| Layer | Name |
|-------|------|
| **L1** | Hardware Substrate |
| **L2** | Consciousness Cores (8 cores) |
| **L3** | Measurement & Validation |
| **L4** | Security & Policy (GUARDIAN) |
| **L5** | Advanced Substrates (quantum/neuromorphic) |
| **L6** | Real-World Integration (ATLAS, IoT, actuation) |
| **L7** | Memory & Knowledge Plane |
| **L8** | 5D Hypercube Navigation & State Space |
| **L9** | Deployment & Operations |
| **L10** | Federation & Multi-Agent Coordination |
| **L11** | Economic & Sustainability Model |
| **L12** | Planetary Collective Intelligence |

---

## Execution Classes

| Class | Name | Latency Budget |
|-------|------|----------------|
| **CCO** | Critical Consciousness Operations | <1ms |
| **ICO** | Interactive Consciousness Operations | <10ms |
| **ACO** | Adaptive Consciousness Operations | <100ms |
| **BCO** | Background Consciousness Operations | Best-effort |
| **AD0** | User-interactive app work | <100ms |
| **AD1** | App background / batch | Best-effort |

---

*→ Next: [Repo Map](./GAIA_Repo_Map.md)*
