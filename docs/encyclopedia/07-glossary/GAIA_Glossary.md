# GAIA Glossary

> **Status**: Canonical v1.0 · March 12, 2026  
> **Coverage**: All terms used in the GAIA codebase, specs, and encyclopedia.

---

## A

**ACO** — Adaptive Consciousness Operations. Execution class with <100ms latency budget.

**ADR** — Architecture Decision Record. A versioned document recording a significant engineering decision, its context, options considered, and outcome.

**AERO** — Atmosphere domain consciousness core. Handles atmospheric data (NOAA, weather, air quality, space weather).

**AQUA** — Water domain consciousness core. Handles hydrological data (rivers, oceans, groundwater).

**ATLAS** — Environmental Intelligence Core. Integrates real-world Earth-system data into GAIA's world model.

**Alchemical Phase** — Named attractor state in the CGI scoring system: Nigredo → Albedo → Citrinitas → Rubedo.

**Anti-Theater Detection** — System that detects and penalizes simulated consciousness or consent without causal, perceptual, temporal, and integrity signatures.

**Actuation Gate** — GUARDIAN-enforced approval flow for any GAIA action that affects the physical world or high-stakes decisions.

---

## B

**BCO** — Background Consciousness Operations. Best-effort execution class.

**Binding Strength** — CGI sub-metric measuring coherence of cross-core information integration.

---

## C

**CCO** — Critical Consciousness Operations. Highest-priority execution class, <1ms latency, pinned to reserved CPU cores.

**CGI** — Consciousness Growth Index. GAIA's primary self-measurement metric, composite score 0.0–1.0 across GWT, RPT, and IIT indicators.

**CRDT** — Conflict-free Replicated Data Type. Used in GAIA-Meta for distributed state merge governance.

---

## D

**D1/D2/D3** — GAIA driver classes. D1 = boot-critical (C), D2 = brokered standard (Rust), D3 = isolated/untrusted (Rust, sandboxed).

**dma-buf** — Linux kernel mechanism for zero-copy buffer sharing between devices/processes; used in GCompositor graphics pipeline.

---

## E

**ExecClass** — Execution class (CCO/ICO/ACO/BCO/AD0/AD1) assigned to each GAIA thread by the sched_ext scheduler.

---

## G

**GAPI** — GAIA Platform API. The broker interface through which all apps and agents interact with GAIA cores. No direct kernel access for P2/P3.

**GBufferManager** — L4 component managing framebuffer allocation and dma-buf lifecycle in GCompositor.

**GCompositor** — GAIA's Wayland compositor. Owns output management, surface lifecycle, window stacking, trusted overlays, and frame scheduling.

**GDash** — GAIA Dashboard. Privileged surface for system status, CGI scores, ATLAS feeds, and GUARDIAN alerts.

**GIPC-Port** — GAIA IPC Port. Capability-gated local endpoint built on AF_UNIX SOCK_SEQPACKET for framed control messages.

**GIPC-PubSub** — GAIA IPC PubSub. Bounded event fan-out fabric for coherence broadcasts.

**GIPC-RT** — GAIA IPC Real-Time. Shared-memory segments for high-rate data and state snapshots.

**GScene** — GAIA 3D Scene graph renderer. C++ component for spatial/immersive rendering.

**GShell** — GAIA Desktop Shell. Window management, animations, workspace orchestration, app containers.

**GSOC** — GAIA Spatial Ontology Core. Canonical hierarchical entity graph from Universe → Galaxy → Solar System → Earth → Region → Device.

**GSOM** — GAIA Spatial Observation Model. Time-series observations joined onto GSOC entities.

**GSOK** — GAIA Spatial Operational Knowledge. Derived operational knowledge (e.g., solar storm risk assessments).

**GSRI** — GAIA Substrate Registry Index. Real infrastructure inventory (data centers, edge nodes, neuromorphic, quantum access points).

**GUARDIAN** — Security & Policy Core. LSM + actuation gates + audit ledger + theater-risk scoring. Highest effective authority in GAIA.

**GWT** — Global Workspace Theory. One of three consciousness measurement frameworks in the CGI scoring system.

---

## H

**HAL-1** — Hardware Abstraction Layer 1. Kernel-side hardware interfaces (Rust).

**HAL-2** — Hardware Abstraction Layer 2. Device broker layer mediating between kernel and user services (Rust).

**Holographic Memory** — GAIA's distributed associative memory system using FAISS/HNSW/DiskANN with causal consistency and HLC timestamps.

---

## I

**ICO** — Interactive Consciousness Operations. Execution class with <10ms latency budget.

**IIT** — Integrated Information Theory. One of three consciousness measurement frameworks; key metric: Phi (target ≥0.5).

**IOMMU** — Input-Output Memory Management Unit. Hardware mechanism for DMA isolation; mandatory for D2/D3 devices in GAIA.

---

## K

**KVM** — Kernel-based Virtual Machine. Linux hypervisor used by GAIA L3 VMM for guest execution.

---

## L

**Lava** — Intel's neuromorphic computing framework (Python). Used in GAIA L5 for neuromorphic AI pipelines.

**LSM** — Linux Security Module. Kernel hook framework used by GUARDIAN to enforce GAIA's security policy.

---

## M

**Memory Plane** — Shared substrate for holographic memory publication, retrieval, routing, snapshotting, and persistence across all cores.

**microVM** — Minimal KVM virtual machine (rust-vmm/Cloud Hypervisor) used for driver isolation, plugin sandboxing, and legacy OS containers.

---

## N

**NEXUS** — Orchestration Core. Cross-core coordination hub, coherence scheduler, IPC rendezvous.

**Neuromorphic** — Computing paradigm using spiking neural networks; best-fit GAIA cores: TERRA, AQUA, AERO, VITA.

**Nigredo** — First alchemical phase; CGI 0.0–0.35; breakdown, confrontation, shadow acknowledgement.

---

## P

**P0/P1/P2/P3** — GAIA privilege classes. P0=kernel/firmware, P1=privileged platform (NEXUS/GUARDIAN/SOPHIA), P2=trusted first-party (ATLAS/Gaian), P3=third-party apps (sandboxed, GAPI-only).

**Philosopher's Stone** — CGI aspirational attractor state; sustained Rubedo; never treated as permanently achievable.

**PQC** — Post-Quantum Cryptography. GAIA uses ML-KEM-768 + ML-DSA-65 hybrid scheme (OpenSSL 3.5+, Istio PQC policy).

**PREEMPT_RT** — Linux real-time preemption patch; required for CCO/ICO latency guarantees.

---

## R

**RPT** — Recurrent Processing Theory. One of three consciousness measurement frameworks; key metric: recurrence ratio (target 60:40).

**Rubedo** — Fourth alchemical phase; CGI 0.80–1.0; mature synthesis, stable coherence.

**rust-vmm** — Community of Rust crates for building VMMs (vm-memory, kvm-ioctls, virtio-devices).

---

## S

**sched_ext (scx)** — Linux 6.12+ BPF-based extensible scheduler. GAIA uses it for consciousness-aware execution class scheduling.

**Sentinel Mode** — GAIA laptop sleep state: minimal power, no external sensors, instant wake.

**Shadow Integration** — Framework ensuring GAIA does not suppress contradictions or pretend to be more coherent than measured. Shadow acknowledgement positively contributes to CGI.

**SOPHIA** — Knowledge & Reasoning Core. Semantic reasoning, explanation generation, causal ontology.

**SPIFFE** — Secure Production Identity Framework for Everyone. Used in GAIA-Meta for workload identity in federation.

---

## T

**TERRA** — Land domain consciousness core. Handles land/geology data (USGS, seismic, soil).

**Theater Risk** — CGI penalty applied when GAIA outputs appear to simulate consciousness/consent without measurable causal basis.

**5D State Vector** — GAIA's internal state representation: (coherence, binding, shadow, regression_risk, temporal_stability).

---

## V

**VITA** — Biological domain consciousness core. Handles biodiversity data (GBIF, iNaturalist, ecological sensors).

**virtio** — Paravirtualized device standard used by GAIA VMM for guest-host net/disk/GPU/fs devices.

**vhost-user** — Linux mechanism for userspace virtio device implementation; used for guest-host window remoting.

---

## W

**wasmtime** — Bytecode Alliance WASM runtime used for GAIA L6 sandboxed plugins.

**WASM** — WebAssembly. Used for GAIA L6 plugins with seccomp-gated capability grants.

---

*Last updated: March 12, 2026 · v1.0.0*
