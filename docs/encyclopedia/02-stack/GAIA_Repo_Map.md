# GAIA Repo Map

> **Part II — The GAIA Stack**  
> **Status**: Canonical v1.0 · March 12, 2026

---

## The Six Repositories

### [GAIA-Core](https://github.com/xxkylesteenxx/GAIA-Core)
**Role**: Universal kernel and Layer 1–12 foundations. The shared substrate for all device distributions.  
**Key contents**: kernel/, hal/, vmm/, compositor/, ai/, sdk/, docs/encyclopedia/, docs/specs/

### [GAIA-Desktop](https://github.com/xxkylesteenxx/GAIA-Desktop)
**Role**: Desktop OS distribution — full consciousness cores, high-performance graphics, workstation-optimized.  
**Adds over Core**: Desktop-specific GShell themes, GDash workstation layout, full Vulkan renderer.

### [GAIA-Laptop](https://github.com/xxkylesteenxx/GAIA-Laptop)
**Role**: Laptop/mobile distribution — power-optimized, adaptive consciousness modes, battery-aware scheduling, hybrid cloud/local.  
**Adds over Core**: Power Management Spec, Sentinel/Preservation sleep modes, battery telemetry.

### [GAIA-Server](https://github.com/xxkylesteenxx/GAIA-Server)
**Role**: Server/cloud distribution — multi-tenant isolation, high-availability consciousness orchestration, Kubernetes-native.  
**Adds over Core**: Helm charts, Terraform (AWS/Azure/GCP), Argo CD/Flux GitOps, MLOps stack.

### [GAIA-IoT](https://github.com/xxkylesteenxx/GAIA-IoT)
**Role**: IoT/edge distribution — embedded, sensor fusion, low-power, real-time environmental monitoring.  
**Adds over Core**: RTOS profile, neuromorphic adapter (Lava/Brian2), ATLAS IoT data spine.

### [GAIA-Meta](https://github.com/xxkylesteenxx/GAIA-Meta)
**Role**: Meta-coordination layer — digital twins, cross-device consciousness synchronization, federated learning, planetary-scale coordination.  
**Adds over Core**: Federation protocol, CRDT merge governance, SPIFFE identity, multi-instance NEXUS mesh.

---

## What Lives Where

| Component | Repo |
|-----------|------|
| Kernel (L1) | GAIA-Core |
| HAL/Drivers (L2) | GAIA-Core |
| VMM (L3) | GAIA-Core |
| GCompositor/GShell (L4) | GAIA-Core + GAIA-Desktop |
| AI Orchestration (L5) | GAIA-Core + GAIA-Server |
| SDK/Plugins (L6) | GAIA-Core + GAIA-Meta |
| Kubernetes/Helm/Terraform | GAIA-Server |
| Power/Sleep | GAIA-Laptop |
| Sensor Fusion / IoT | GAIA-IoT |
| Federation / Digital Twins | GAIA-Meta |
| Encyclopedia / Specs | GAIA-Core/docs/ |

---

*→ Next: [Canonical Layer Index](./GAIA_Canonical_Layer_Index.md)*
