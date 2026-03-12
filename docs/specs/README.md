# GAIA-Core Specification Index

This directory contains all canonical specifications for the GAIA project. Specs are organized by domain. Flat-root copies of some specs exist for legacy reasons; the subdirectory paths are canonical.

---

## Kernel & Systems

| Spec | Path | Status |
|---|---|---|
| Linux Kernel Modifications | [`kernel/GAIA_Linux_Kernel_Modifications_Spec_v1.0.md`](kernel/GAIA_Linux_Kernel_Modifications_Spec_v1.0.md) | Draft v1.0 |
| Inter-Process Communication | [`ipc/GAIA_Inter_Process_Communication_Spec_v1.0.md`](ipc/GAIA_Inter_Process_Communication_Spec_v1.0.md) | Draft v1.0 |

## Memory & Cognition

| Spec | Path | Status |
|---|---|---|
| Holographic Memory Architecture | [`memory/GAIA_Holographic_Memory_Architecture_Spec_v1.0.md`](memory/GAIA_Holographic_Memory_Architecture_Spec_v1.0.md) | Draft v1.0 (patched) |
| Consciousness Measurement & Validation | [`consciousness/GAIA_Consciousness_Measurement_Validation_Spec_v1.0.md`](consciousness/GAIA_Consciousness_Measurement_Validation_Spec_v1.0.md) | Draft v1.0 |

## Neuromorphic Hardware

| Spec | Path | Status |
|---|---|---|
| Neuromorphic Hardware Integration | [`neuromorphic/GAIA_Neuromorphic_Hardware_Integration_Spec_v1.0.md`](neuromorphic/GAIA_Neuromorphic_Hardware_Integration_Spec_v1.0.md) | Draft v1.0 |

## Environmental Cores (TERRA / AQUA / AERO / VITA)

| Spec | Path | Status |
|---|---|---|
| Environmental Data Quality | [`environmental/GAIA_Environmental_Data_Quality_Spec_v1.0.md`](environmental/GAIA_Environmental_Data_Quality_Spec_v1.0.md) | Draft v1.0 |

## Energy & Optimization

| Spec | Path | Status |
|---|---|---|
| Energy Optimization | [`energy/GAIA_Energy_Optimization_Spec_v1.0.md`](energy/GAIA_Energy_Optimization_Spec_v1.0.md) | Draft v1.0 |

## Coordination & Federation

| Spec | Path | Status |
|---|---|---|
| Planetary Multi-Agent Coordination | [`coordination/GAIA_Planetary_Multi_Agent_Coordination_Spec_v1.0.md`](coordination/GAIA_Planetary_Multi_Agent_Coordination_Spec_v1.0.md) | Draft v1.0 |
| Synergy Measurement Framework | [`synergy/GAIA_Synergy_Measurement_Framework_Spec_v1.0.md`](synergy/GAIA_Synergy_Measurement_Framework_Spec_v1.0.md) | Draft v1.0 |

## Security

| Spec | Path | Status |
|---|---|---|
| Post-Quantum Cryptography Deployment | [`security/pqc/GAIA_Post_Quantum_Cryptography_Production_Deployment_Spec_v1.0.md`](security/pqc/GAIA_Post_Quantum_Cryptography_Production_Deployment_Spec_v1.0.md) | Draft v1.0 |

## Packaging & Repository Governance

| Spec | Path | Status |
|---|---|---|
| Cross-Repo Packaging & Dependency Resolution | [`packaging/GAIA_Cross_Repo_Packaging_Dependency_Resolution_Spec_v1.0.md`](packaging/GAIA_Cross_Repo_Packaging_Dependency_Resolution_Spec_v1.0.md) | Draft v1.0 |

## Inference & Runtime Contracts

| Spec | Path | Status |
|---|---|---|
| Inference Contract Reconciliation | [`inference/GAIA_Inference_Contract_Reconciliation_Spec_v1.0.md`](inference/GAIA_Inference_Contract_Reconciliation_Spec_v1.0.md) | Draft v1.0 |

## Implementation Plans & Gap Analysis

| Document | Path | Status |
|---|---|---|
| Gap Resolution Matrix | [`GAIA_Gap_Resolution_Matrix_v1.0.md`](GAIA_Gap_Resolution_Matrix_v1.0.md) | v1.0 |
| Remediation Execution Plan | [`GAIA_Remediation_Execution_Plan_v1.0.md`](GAIA_Remediation_Execution_Plan_v1.0.md) | v1.0 |
| Substrate Resolution & Setup Plan | [`GAIA_Substrate_Resolution_and_Setup_Plan_v1.0.md`](GAIA_Substrate_Resolution_and_Setup_Plan_v1.0.md) | v1.0 |
| Tier 1 Implementation Plan | [`GAIA_Tier1_Implementation_Plan_v1.0.md`](GAIA_Tier1_Implementation_Plan_v1.0.md) | v1.0 |
| Tier 2 Implementation Plan | [`GAIA_Tier2_Implementation_Plan_v1.0.md`](GAIA_Tier2_Implementation_Plan_v1.0.md) | v1.0 |
| Tier 3 Implementation Plan | [`GAIA_Tier3_Implementation_Plan_v1.0.md`](GAIA_Tier3_Implementation_Plan_v1.0.md) | v1.0 |
| Tier 1 Blockers Research Plan | [`GAIA_Tier1_Blockers_Research_and_Implementation_Plan.md`](GAIA_Tier1_Blockers_Research_and_Implementation_Plan.md) | v1.0 |
| Tier 2 Deployment Blockers Plan | [`GAIA_Tier2_Deployment_Blockers_Research_and_Implementation_Plan.md`](GAIA_Tier2_Deployment_Blockers_Research_and_Implementation_Plan.md) | v1.0 |
| Tier 3 Validation Blockers Plan | [`GAIA_Tier3_Validation_Blockers_Research_and_Implementation_Plan.md`](GAIA_Tier3_Validation_Blockers_Research_and_Implementation_Plan.md) | v1.0 |

---

## Known Gaps — Specs Not Yet Written

The following specs are **referenced** by existing documents but do not yet exist. These are the next priority items:

| Missing Spec | Referenced By | Priority |
|---|---|---|
| GUARDIAN LSM Spec | Kernel Modifications Spec | 🔴 Critical |
| Multimodal Memory Substrate Spec | Holographic Memory Spec (patched) | 🔴 Critical |
| Consciousness Continuity / Identity Persistence Spec | Consciousness Measurement Spec, GAIA OS Thread | 🟠 High |
| Digital Twin Synchronization Spec | GAIA-Meta scope, Multi-Agent Coordination Spec | 🟠 High |
| Plugin / Extension Security Spec | ATLAS scope, GAIA OS Thread | 🟠 High |
| Jurisdiction Engine Spec | Tier 2 Blockers Plan | 🟡 Medium |
| GAIA Observability / Telemetry Spec | Tier 1/2 Plans | 🟡 Medium |
| Cross-Repo Dependency Map | All repos | 🟡 Medium — partially addressed by PKG-001 |

---

*Last updated: 2026-03-11 — added Remediation Execution Plan v1.0*
