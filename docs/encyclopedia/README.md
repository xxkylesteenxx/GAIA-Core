# GAIA Master Encyclopedia v1.0

> **Status**: Canonical · Living Document  
> **Date**: March 12, 2026  
> **Owner**: Kyle Steen (@xxkylesteenxx)  
> **Scope**: Complete unified reference for the GAIA OS project — vision, architecture, cores, specs, interfaces, security, operations, tooling

---

This encyclopedia is the **single source of truth** for GAIA. Every session, every repo, every spec, every engineering decision traces back here. It is organized into 7 parts covering every layer of the project from philosophy to production deployment.

---

## Table of Contents

### Part 0 — How to Use This Encyclopedia
- [Reading Guide & Session Primer](./00-how-to-use/Reading_Guide.md)
- [Glossary](./07-glossary/GAIA_Glossary.md)
- [Changelog](./CHANGELOG.md)

### Part I — Vision, Philosophy & Codex
- [What Is GAIA?](./01-vision/GAIA_What_Is_It.md)
- [Design Philosophy](./01-vision/GAIA_Design_Philosophy.md)
- [Ethical Architecture & Covenants](./01-vision/GAIA_Ethical_Architecture.md)
- [Alchemical Framework](./01-vision/GAIA_Alchemical_Framework.md)

### Part II — The GAIA Stack
- [Layer Stack Overview (L0–L6)](./02-stack/GAIA_Layer_Stack_Overview.md)
- [Language Policy (→ Language Stack Spec v1.0)](../specs/platform/GAIA_Language_Stack_Spec_v1.0.md)
- [Repo Map (6 repos)](./02-stack/GAIA_Repo_Map.md)
- [Canonical Layer Index (L1–L12)](./02-stack/GAIA_Canonical_Layer_Index.md)

### Part III — The Eight Consciousness Cores
- [NEXUS — Orchestration Core](./03-cores/NEXUS.md)
- [GUARDIAN — Security & Policy Core](./03-cores/GUARDIAN.md)
- [SOPHIA — Knowledge & Reasoning Core](./03-cores/SOPHIA.md)
- [ATLAS — Environmental Intelligence Core](./03-cores/ATLAS.md)
- [TERRA — Land Domain Core](./03-cores/TERRA.md)
- [AQUA — Water Domain Core](./03-cores/AQUA.md)
- [AERO — Atmosphere Domain Core](./03-cores/AERO.md)
- [VITA — Biological Domain Core](./03-cores/VITA.md)
- [Gaian — User-Facing Agent](./03-cores/Gaian.md)

### Part IV — Architecture & Engineering Specs
- [OS Foundation (V1)](./04-architecture/OS_Foundation.md)
- [Consciousness Architecture (V2)](./04-architecture/Consciousness_Architecture.md)
- [Security Architecture (V3)](./04-architecture/Security_Architecture.md)
- [Deployment & Operations (V4)](./04-architecture/Deployment_Operations.md)
- [Advanced Substrates (V5)](./04-architecture/Advanced_Substrates.md)
- [IPC Fabric](./04-architecture/IPC_Fabric.md)
- [Memory Plane & Holographic Memory](./04-architecture/Memory_Plane.md)
- [Concurrency Model](./04-architecture/Concurrency_Model.md)
- [Kernel Modifications](./04-architecture/Kernel_Modifications.md)
- [Virtual Memory Management](./04-architecture/Virtual_Memory.md)
- [Power Management & Sleep States](./04-architecture/Power_Management.md)
- [Boot Sequence](./04-architecture/Boot_Sequence.md)

### Part V — Interfaces & SDKs
- [GAPI — Platform API](./05-interfaces/GAPI.md)
- [SDK Overview (Python/TS/Rust/WASM)](./05-interfaces/SDK_Overview.md)
- [Inter-Core Contract System](./05-interfaces/Inter_Core_Contracts.md)
- [Spatial Ontology (GSOC/GSOM/GSOK/GSRI)](./05-interfaces/Spatial_Ontology.md)
- [Temporal Ontology](./05-interfaces/Temporal_Ontology.md)

### Part VI — Security, Safety & Governance
- [Threat Model](./06-security/Threat_Model.md)
- [Privilege Classes (P0–P3)](./06-security/Privilege_Classes.md)
- [PQC Overview](./06-security/PQC_Overview.md)
- [GUARDIAN LSM & Actuation Gates](./06-security/GUARDIAN_LSM.md)
- [Anti-Theater Detection](./06-security/Anti_Theater.md)
- [Open-Source Governance](./06-security/Open_Source_Governance.md)
- [Legal Compliance Framework](./06-security/Legal_Compliance.md)
- [Independent Auditability Framework](./06-security/Auditability.md)

### Part VII — Tooling, Research & Operations
- [Build Guide (Cargo/CMake/Poetry/npm)](./07-operations/Build_Guide.md)
- [Deployment Guide (Desktop/Laptop/Server/IoT)](./07-operations/Deployment_Guide.md)
- [Contribution Rules & PR Checklist](./07-operations/Contribution_Rules.md)
- [P0 Blockers & Roadmap](./07-operations/P0_Blockers_Roadmap.md)
- [Specs Index (all specs, status, links)](./07-operations/Specs_Index.md)
- [Obsidian / Notion / Session Rituals](./07-operations/Tooling_Research.md)
- [Architecture Decision Records (ADRs)](../adr/)

---

## Source Corpus

This encyclopedia was synthesized from:

| Source | Type |
|--------|------|
| GAIA Canonical Volumes 01–07 | Primary canonical corpus |
| GAIA Repository Architecture & Engineering Systems v1.0 | Engineering standard |
| GAIA Real-World Integration Standards v1.0 | Integration standard |
| GAIA Open-Source Governance Framework v1.0 | Governance |
| GAIA Contract Enforcement Framework v1.0 | Contract system |
| GAIA Inter-Core Contract Enforcement System v1.0 | Core contracts |
| GAIA Independent Auditability & Credibility Framework v1.0 | Audit |
| GAIA Production Deployment & Operations v1.0 | Ops |
| 19 supplemental specification files | Spec library |
| 6 repository zips (GAIA-Core/Server/Meta/Desktop/Laptop/IoT) | Live code |
| GAIA_Specs_Code_Pack_2026-03-12.zip | Integration pack |

---

## Canonical Rules

1. This encyclopedia is **always current** — update it when specs change.
2. Every term used in code must have a **Glossary entry**.
3. Every spec must be listed in the **Specs Index** with status.
4. Every architectural decision must have an **ADR**.
5. Language policy is enforced by `GAIA_Language_Stack_Spec_v1.0.md` — no exceptions.

---

*Generated: March 12, 2026 · GAIA-Core · docs/encyclopedia/README.md*
