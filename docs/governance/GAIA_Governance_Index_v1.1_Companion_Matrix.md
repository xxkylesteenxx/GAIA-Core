# GAIA Governance Index v1.1 — Companion Adoption Matrix

*Compiled by: Societas AI Research Team*
*Date: March 14, 2026*
*Classification: Canonical Companion to GAIA Governance Index v1.1*

---

## Purpose

This matrix provides a practical, repository- and CI/CD-oriented reference for engineering teams implementing GAIA Governance Index v1.1. It maps each canonical document to the repositories, CI checks, and system components where its requirements must be enforced.

---

## Document × Repository Matrix

| Document | GAIA-Core | GAIA-Server | GAIA-IoT | GAIA-Apps | GAIA-Docs |
|----------|:---------:|:-----------:|:--------:|:---------:|:---------:|
| Safety-Critical Systems Policy v1.0 | ✅ Required | ✅ Required | ✅ Required | ✅ Required | 📄 Reference |
| Biomedical Interface and Biosafety Spec v1.0 | ✅ Required | ✅ Required | ✅ Required | ✅ Required | 📄 Reference |
| Secure Compute and Verification Spec v1.0 | ✅ Required | ✅ Required | ✅ Required | ✅ Required | 📄 Reference |
| Applied Sciences Knowledge Graph Spec v1.0 | ✅ Required | ✅ Required | ⚠️ Partial | ⚠️ Partial | 📄 Reference |
| Infrastructure Digital Twin Spec v1.0 | ⚠️ Partial | ✅ Required | ✅ Required | ⚠️ Partial | 📄 Reference |
| Habitat and Food Systems Intelligence Spec v1.0 | ⚠️ Partial | ✅ Required | ⚠️ Partial | ⚠️ Partial | 📄 Reference |
| Contract Enforcement Framework v1.0 | ✅ Required | ✅ Required | ✅ Required | ✅ Required | 📄 Reference |
| Auditability and Credibility Framework v1.0 | ✅ Required | ✅ Required | ✅ Required | ✅ Required | 📄 Reference |

**Legend:**
- ✅ Required — full compliance required for production deployment
- ⚠️ Partial — applicable sections required; engineering lead determines scope
- 📄 Reference — informational; no CI gate required

---

## CI/CD Gate Requirements by Tier

### Tier 1 Gates (must block merge/deploy if failing)

| Check | Trigger | Enforced By |
|-------|---------|-------------|
| Safety class assigned to all new services | PR open | GUARDIAN policy check |
| Biomedical capability class assigned to biomedical features | PR open | GUARDIAN policy check |
| Signed artifact present | Release | Secure Compute pipeline |
| SBOM generated | Release | Secure Compute pipeline |
| Provenance metadata attached | Release | Secure Compute pipeline |
| Vulnerability scan pass (no unreviewed critical CVEs) | Every build | CI scanner |
| Hazard record present for S2+ systems | Release | Safety policy gate |
| B2+ biomedical review triggered | PR with biomedical label | VITA core review process |

### Tier 2 Gates (must pass before production; advisory on PRs)

| Check | Trigger | Enforced By |
|-------|---------|-------------|
| SHACL validation pass for graph additions | Graph commit | Knowledge Graph pipeline |
| Evidence tier attached to all new graph claims | Graph commit | Knowledge Graph pipeline |
| Twin quality index defined for new twin services | Service registration | Digital Twin pipeline |
| Sync class declared for all twin data feeds | Service registration | Digital Twin pipeline |
| Habitat output uncertainty disclosure present | Habitat service release | Habitat spec compliance check |

### Tier 3 Gates (required for externally-facing deployments)

| Check | Trigger | Enforced By |
|-------|---------|-------------|
| Audit log integrity check | Deployment | Auditability framework |
| Independent review record present for S3/S4 systems | Release | Safety policy gate |
| Public graph release signed by GUARDIAN | Graph release | Knowledge Graph pipeline |

---

## Core × Document Responsibility Matrix

| Core | Primary Docs | Key Obligations |
|------|-------------|----------------|
| NEXUS | Governance Index, Contract Enforcement | orchestration, identity, cross-core mediation, index registry |
| SOPHIA | Knowledge Graph Spec | ontology stewardship, evidence tier enforcement, reasoning governance |
| GUARDIAN | Safety Policy, Biomedical Spec, Secure Compute Spec, Governance Index | policy enforcement, release gating, GUARDIAN sign-off, alert routing |
| TERRA | Habitat Spec, Digital Twin Spec | soil/land/ecosystem state, habitat unit ownership |
| AQUA | Habitat Spec, Digital Twin Spec | water systems, watershed modeling, twin data feeds |
| AERO | Habitat Spec, Digital Twin Spec | atmospheric data, climate context, weather feeds |
| VITA | Biomedical Spec, Habitat Spec | clinical interfaces, biosafety enforcement, One Health linkage |
| URBS | Digital Twin Spec, Habitat Spec | built environment, infrastructure twins, urban food access |
| ETA | Safety Policy, Secure Compute Spec | energy systems, thermodynamics, compute resource optimization |

---

## Expected Baseline Artifacts — Readiness Tracker

These are the Tier 0 constitutional companions declared in the Governance Index but not yet physically present in the working corpus. This tracker supports the next governance cycle.

| Artifact | Status | Priority | Owner |
|----------|--------|----------|-------|
| GAIA Product Boundary Spec | ❌ Not yet created | P0 | Engineering Council |
| GAIA Scope Matrix | ❌ Not yet created | P0 | Engineering Council |
| GAIA Boundary Compliance Header Standard | ❌ Not yet created | P0 | Engineering Council |
| Gaian v1 Architecture Spec | ❌ Not yet created | P0 | Engineering Council |
| ATLAS v1 Scope Note Patch Template | ❌ Not yet created | P0 | Engineering Council |

---

## Document Adoption Priority Order

For teams beginning GAIA governance adoption, implement in this order:

1. **Safety-Critical Systems Policy** — classify all existing services by safety class immediately
2. **Secure Compute and Verification Spec** — enable signed releases and SBOM generation
3. **Biomedical Interface and Biosafety Spec** — classify all biomedical-adjacent features
4. **Applied Sciences Knowledge Graph Spec** — enforce evidence tier and SHACL validation on new graph additions
5. **Infrastructure Digital Twin Spec** — register all existing twins and assign quality indices
6. **Habitat and Food Systems Intelligence Spec** — ensure uncertainty disclosure on all habitat and food outputs
7. **Create Tier 0 expected baseline artifacts** — complete the constitutional layer
8. **GAIA Master Implementation Roadmap** — map all specs to repos, owners, and milestones

---

## Next Governance Cycle Triggers

Governance Index v1.2 should be initiated when any of the following occur:

- A Tier 0 expected baseline artifact is created
- The GAIA Master Implementation Roadmap is published
- The Product Boundary and Actuation Scope Update is published
- A new consciousness core (e.g., URBS, ETA) is formally ratified
- A Tier 1 policy incident occurs requiring policy revision
