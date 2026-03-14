# GAIA Governance Index v1.1 — Companion Matrix
**Quick Authority Crosswalk, Integration Register, and Implementation Hooks**

*Compiled by: Societas AI Research Team*
*Date: March 14, 2026*
*Classification: P1 Critical - Governance Companion*

---

## Purpose

This matrix provides a practical, repository- and CI/CD-oriented reference for engineering teams implementing GAIA Governance Index v1.1. It maps each canonical document to the repositories, CI checks, and system components where its requirements must be enforced.

---

## 1. Quick Authority Crosswalk

| Domain / Situation | Highest Governing Document(s) | Blocking Controls Before Release |
|---|---|---|
| general repository architecture | Governance Index v1.1; Open-Source Governance Framework v1.0; Repository Architecture and Engineering Systems v1.0 | contract enforcement, auditability, deployment gating |
| any safety-relevant feature | Safety-Critical Systems Policy v1.0 | hazard analysis, verification, safe-state design, release gate |
| trusted production compute | Secure Compute and Verification Spec v1.0 | attestation, artifact provenance, signing, least privilege |
| biomedical data / workflow / biosurveillance | Biomedical Interface and Biosafety Spec v1.0 | boundary review, human authority, refusal/escalation logic |
| knowledge graph / ontology / canonical claims | Applied Sciences Knowledge Graph Spec v1.0 | provenance, ontology review, graph release management |
| infrastructure twins / facilities / utilities / transport | Infrastructure Digital Twin Spec v1.0 | bounded trust, synchronization quality, scenario separation |
| habitat / food / soil / water / One Health intelligence | Habitat and Food Systems Intelligence Spec v1.0 | locale-specific evidence, coupled-system review |

---

## 2. New Spec Registration Entries

### 2.1 GAIA Safety-Critical Systems Policy v1.0
- **tier:** 2
- **classification:** P0
- **binding scope:** all systems that can affect health, infrastructure, environment, emergencies, or critical resource allocation
- **actuation stance:** restrictive
- **release status effect:** may block release

### 2.2 GAIA Secure Compute and Verification Spec v1.0
- **tier:** 2
- **classification:** P0
- **binding scope:** protected build, deployment, runtime, and trust domains
- **actuation stance:** indirect but mandatory for trusted operation
- **release status effect:** may block admission to trusted environments

### 2.3 GAIA Biomedical Interface and Biosafety Spec v1.0
- **tier:** 2
- **classification:** P0
- **binding scope:** biomedical, clinical, biosurveillance, biological-model-adjacent systems
- **actuation stance:** restrictive
- **release status effect:** may block biomedical capability exposure

### 2.4 GAIA Applied Sciences Knowledge Graph Spec v1.0
- **tier:** 3
- **classification:** P1
- **binding scope:** canonical semantics, graph release, provenance, ontology
- **actuation stance:** none by itself
- **release status effect:** blocks incompatible ontology or provenance-breaking changes

### 2.5 GAIA Infrastructure Digital Twin Spec v1.0
- **tier:** 3
- **classification:** P1
- **binding scope:** built-environment and utility twin systems
- **actuation stance:** bounded and non-authorizing
- **release status effect:** blocks twin claims lacking trust, time, or scenario disclosure

### 2.6 GAIA Habitat and Food Systems Intelligence Spec v1.0
- **tier:** 3
- **classification:** P1
- **binding scope:** habitat, soil, water, agrifood, livability, One Health intelligence
- **actuation stance:** advisory unless separately authorized
- **release status effect:** blocks oversimplified or decontextualized decision logic

---

## 3. Machine-Readable Spec Registry

```yaml
gaia_spec_registry:
  - document_id: "gaia-governance-index-v1.1"
    title: "GAIA Governance Index v1.1"
    tier: 2
    classification: "P0"
    status: "active"
    canonical: true
    blocking: true
  - document_id: "gaia-safety-critical-systems-policy-v1.0"
    title: "GAIA Safety-Critical Systems Policy v1.0"
    tier: 2
    classification: "P0"
    status: "active"
    canonical: true
    blocking: true
  - document_id: "gaia-secure-compute-and-verification-spec-v1.0"
    title: "GAIA Secure Compute and Verification Spec v1.0"
    tier: 2
    classification: "P0"
    status: "active"
    canonical: true
    blocking: true
  - document_id: "gaia-biomedical-interface-and-biosafety-spec-v1.0"
    title: "GAIA Biomedical Interface and Biosafety Spec v1.0"
    tier: 2
    classification: "P0"
    status: "active"
    canonical: true
    blocking: true
  - document_id: "gaia-applied-sciences-knowledge-graph-spec-v1.0"
    title: "GAIA Applied Sciences Knowledge Graph Spec v1.0"
    tier: 3
    classification: "P1"
    status: "active"
    canonical: true
    blocking: true
  - document_id: "gaia-infrastructure-digital-twin-spec-v1.0"
    title: "GAIA Infrastructure Digital Twin Spec v1.0"
    tier: 3
    classification: "P1"
    status: "active"
    canonical: true
    blocking: true
  - document_id: "gaia-habitat-and-food-systems-intelligence-spec-v1.0"
    title: "GAIA Habitat and Food Systems Intelligence Spec v1.0"
    tier: 3
    classification: "P1"
    status: "active"
    canonical: true
    blocking: true
```

---

## 4. Document × Repository Matrix

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

## 5. CI/CD Gate Requirements by Tier

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

## 6. Immediate Repository Hooks

Add the following checks to CI/CD immediately:

- verify every protected service declares governing document IDs;
- block release if Tier 2 dependencies are missing from service metadata;
- block graph schema changes without provenance and ontology review;
- block biomedical service rollout without explicit boundary class and human authority declaration;
- block trusted-environment deployment without attestation evidence.

---

## 7. Core × Document Responsibility Matrix

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

## 8. Expected Baseline Artifacts — Readiness Tracker

These are the Tier 0 constitutional companions declared in the Governance Index but not yet physically present in the working corpus.

| Artifact | Status | Priority | Owner |
|----------|--------|----------|-------|
| GAIA Product Boundary Spec | ❌ Not yet created | P0 | Engineering Council |
| GAIA Scope Matrix | ❌ Not yet created | P0 | Engineering Council |
| GAIA Boundary Compliance Header Standard | ❌ Not yet created | P0 | Engineering Council |
| Gaian v1 Architecture Spec | ❌ Not yet created | P0 | Engineering Council |
| ATLAS v1 Scope Note Patch Template | ❌ Not yet created | P0 | Engineering Council |

---

## 9. Document Adoption Priority Order

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

## 10. Next Governance Cycle Triggers

Governance Index v1.2 should be initiated when any of the following occur:

- A Tier 0 expected baseline artifact is created
- The GAIA Master Implementation Roadmap is published
- The Product Boundary and Actuation Scope Update is published
- A new consciousness core (e.g., URBS, ETA) is formally ratified
- A Tier 1 policy incident occurs requiring policy revision

---

## Release Note

This companion file is subordinate to **GAIA Governance Index v1.1** and exists to accelerate repository adoption and policy-as-code implementation.
