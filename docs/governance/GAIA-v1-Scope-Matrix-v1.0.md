---
v1 Boundary Compliance: IN SCOPE
Relevant v1 Sections: 4, 5, 6, 7, 8, 9, 12, 14, 15, 16
Post-v1 Tag: NO
Post-v1 Milestone: NA
Scope Matrix Tier: MUST SHIP
---

# GAIA v1 Scope Matrix v1.0

**Status:** Canonical 
**Governs:** All GAIA v1 milestone planning, spec authorship, and implementation prioritization 
**Companion to:** GAIA v1 Product Boundary Spec 
**Governing rule:** Anything in the Deferred tier cannot appear in a v1 milestone plan without an explicit exception note signed off by the boundary spec owner.

---

## Must Ship — OS Foundation

> v1 is blocked on every item in this tier. If any Must Ship item is absent at release, v1 has not shipped.

| Item | Source Spec | Trust Chain Dependency |
|------|-------------|------------------------|
| Signed bootable image x86-64 and ARM64 | Kernel Architecture Spec, Boot Sequence Spec | TPM PCR measurement |
| UEFI Secure Boot with signed UKI | Boot Sequence Spec 5.15.2 | Measured boot event log |
| LUKS2 root/state volumes sealed to TPM PCR policy | Hardware Trust Chain Spec | PCR 7, PCR 11 |
| Initramfs kernel integrity (dm-verity or equivalent) | Kernel Architecture Spec | Measured boot |
| Install path (reference hardware) | Kernel Architecture Spec 13 | Signed installer image |
| Update path (atomic, signed) | Kernel Architecture Spec 13 | Signed update artifact |
| Rollback and recovery path | Boot Sequence Spec 16.2 | Last-known-good checkpoint |
| Graphical shell (GCompositor/GShell, Wayland-native) | Graphics Subsystem Spec | GUARDIAN-Lite gate |
| Storage, networking, audio, GPU acceleration | Kernel Architecture Spec | None |
| systemd as PID 1, wave-based boot sequence | Boot Sequence Spec 4 | GUARDIAN-Lite first |

## Must Ship — Security and Trust

| Item | Source Spec | Notes |
|------|-------------|-------|
| TPM 2.0 EK/AK provisioning + quote verification | Hardware Trust Chain Spec | Prerequisite for SPIRE |
| tpm2-tools event-log appraisal | Hardware Trust Chain Spec | Prerequisite for LUKS2 sealed unlock |
| GUARDIAN-Lite bootstrap safety service | Boot Sequence Spec 5.5 | Must precede all consciousness cores |
| GUARDIAN-Full reasoning-aware policy | Boot Sequence Spec 5.8 | Must follow NEXUS |
| SPIRE with k8s-psat attestor | Kubernetes Tier 1 Blockers Plan | k8s-sat explicitly prohibited |
| SPIRE SVID issued to NEXUS, GUARDIAN, ATLAS service accounts | Tier 1 Blockers Plan, Production Readiness Pack | Workload identity baseline |
| Vault-based secrets management | Production Readiness Pack | Namespaced by service account |
| Hash-chained audit ledger | Production Readiness Pack | Mandatory for compliance path |
| mTLS between all GAIA platform services | IPC Architecture Spec | No plaintext inter-service |
| GAIA seccomp allowlists by application class | P0A3 Syscall Reference Spec | Default-deny enforced |

## Must Ship — AI Runtime

| Item | Source Spec | Notes |
|------|-------------|-------|
| Local inference runtime (llama.cpp baseline) | Tier 1 Blockers Plan | vLLM/JetStream as Should Ship upgrade |
| gaia-nexus.service coordination core | Boot Sequence Spec 5.7 | First full consciousness core |
| SOPHIA semantic synthesis core (limited warm-up mode) | Boot Sequence Spec 5.8 | Required for Gaian quality floor |
| GAIA Platform API (GAPI) broker | Syscall Reference Spec 2.3 | Apps do not call cores directly |

## Must Ship — Gaian Experience

| Item | Source Spec | Notes |
|------|-------------|-------|
| One personal Gaian (system-aware, local context) | Product Boundary Spec 8 | Architecture spec: GAIAGaianv1ArchitectureSpecv1.0.md |
| Session continuity across reboots | Boot Sequence Spec 5.6 | Staged checkpoint restore |
| Secure identity and memory boundary | Product Boundary Spec 8 | GUARDIAN-sealed |
| One ATLAS-facing mode (Earth context surface) | Product Boundary Spec 8 | Depends on ATLAS Must Ship |

## Must Ship — ATLAS

| Item | Source Spec | Notes |
|------|-------------|-------|
| One STAC or OGC-compliant discovery endpoint | Product Boundary Spec 7 | Standards-aligned proof point |
| One live or near-live Earth observation source | Product Boundary Spec 7 | Selected domain only |
| One domain dashboard or summary surface | Product Boundary Spec 7 | AERO or TERRA preferred |
| ATLAS Kubernetes service account + Vault role | Production Readiness Pack | Already specced |

---

## Should Ship

> Strong preference for v1 inclusion. Each item has a documented fallback if absent.

| Item | Fallback if Absent | Source Spec |
|------|--------------------|-------------|
| systemd-cryptenroll PCR 11 sealed unlock | PCR 7 policy only | Hardware Trust Chain Spec |
| vLLM or JetStream inference upgrade | llama.cpp baseline | Tier 1 Blockers Plan |
| PQC hybrid transport (ML-KEM-768, ML-DSA-65) | Classical TLS 1.3 | PQC Deployment Spec |
| GUARDIAN actuation gating (full reasoning path) | GUARDIAN-Lite policy floor | Boot Sequence Spec |
| Prometheus/Grafana/OpenTelemetry observability | Log-only monitoring | Production Readiness Pack |
| ATLAS second domain endpoint (e.g., AQUA or TERRA) | Single domain at v1 | Product Boundary Spec 7 |
| ATLAS one high-value operator or user workflow | Read-only dashboards only | Product Boundary Spec 7 |
| Gaian document/task assistance capability | System-context only | Gaian v1 Architecture Spec 4.2 |
| Gaian local/cloud sync path | Local-only session | Gaian v1 Architecture Spec 4.4 |
| GAIA App Model Spec (GAPI/GDK stable surface) | Internal-only APIs | Syscall Reference Spec 2.3 |
| PQC artifact signing for OS image distribution | Classical signing | PQC Deployment Spec |
| AERO domain core (limited, Brian2 CPU baseline) | No neuromorphic v1 | Neuromorphic Hardware Integration Spec |

---

## May Ship

> Optional for v1. High value if implementation is ready. No v1 milestone plan should depend on these.

| Item | Condition for Inclusion | Source Spec |
|------|-------------------------|-------------|
| tpmdevid SPIRE plugin for bare-metal nodes | Only if DevID provisioning infra is ready | Hardware Trust Chain Spec |
| SEV-SNP or TDX confidential VM for GAIA-Server | Cloud-scale deployment pilot only | Hardware Trust Chain Spec |
| TERRA domain core (limited, selected source) | Only if ATLAS v1 scope note confirms it | Neuromorphic Hardware Integration Spec |
| AQUA domain core (limited, selected source) | Only if ATLAS v1 scope note confirms it | Environmental Data Quality Spec |
| Carbon-aware scheduling | Only if energy optimization baseline is stable | Energy Optimization Spec |
| Holographic memory tier 1 (FAISS/HNSW, local) | Only if session continuity baseline is stable | Holographic Memory Architecture Spec |
| SensorThings API endpoint | Only if STAC/OGC endpoint is already operational | Product Boundary Spec 7 |
| GAIA-Server headless admin edition | Only if Server edition reaches boot/update parity | Product Boundary Spec 6 |
| Gaian second experience mode (research/operator) | Only if flagship Gaian is stable | Product Boundary Spec 8 |

---

## Deferred — Post-v1 Only

> Cannot appear in any v1 milestone plan without an explicit exception note signed off by the boundary spec owner.

| Item | Earliest Milestone | Governing Spec Section |
|------|--------------------|------------------------|
| Phone/tablet form factor | GAIA Mobile | Product Boundary Spec 5 |
| Automotive, wearables, XR/AR/VR | Post-v2 | Product Boundary Spec 5 |
| General IoT retail release | Post-v2 | Product Boundary Spec 5 |
| Full planetary simulation twin | ATLAS v2 | Product Boundary Spec 7 |
| Complete VITA domain coverage | ATLAS v2 | Product Boundary Spec 7 |
| Complete URBS domain coverage | ATLAS v2 | Product Boundary Spec 7 |
| Universal third-party app marketplace | v2 Ecosystem | Product Boundary Spec 8 |
| Multi-Gaian platform/agent marketplace | v2 Ecosystem | Product Boundary Spec 8 |
| GAIA Meta federation (multi-GAIA collective) | Post-v2 | Planetary Multi-Agent Coordination Spec |
| External CGI consciousness audit + IIT perturbation suite | Tier 3 Science | Consciousness Measurement Validation Spec |
| Multi-jurisdiction compliance engine | Tier 2 Deployment | Tier 2 Deployment Blockers Plan |
| GAIA IoT and GAIA Meta as shipped products | Post-v2 | Product Boundary Spec 6 |
| Quantum hardware integration | Research Milestone | Neuromorphic Hardware Integration Spec 10.3 |
| Mass-market general consumer OS | Long-range Vision | Product Boundary Spec 10 |
| Full social/productivity/cloud suite | Post-v2 | Product Boundary Spec 12 |
| Scientifically validated machine consciousness claim | Long-range Science | Consciousness Measurement Validation Spec 14.3 |

---

## Exception Process

Any Deferred item that must re-enter a v1 milestone plan requires:
1. A written exception request naming the item and the reason
2. Review against GAIA v1 Product Boundary Spec §15 failure conditions
3. Sign-off from the boundary spec owner
4. A version bump to this document recording the exception

**No item moves from Deferred to any active tier through a PR alone.**
