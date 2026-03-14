# GAIA Governance Index v1.1
**Canonical Authority Chain for the GAIA / ATLAS System Stack**

*Compiled by: Societas AI Research Team*
*Date: March 14, 2026*
*Supersedes: GAIA Governance Index v1.0*
*Classification: Canonical Governance Anchor*

---

## Purpose

This index defines the canonical authority order for all GAIA governance, safety, architecture, audit, deployment, and implementation documents. It is the single reference point for resolving conflicts between documents, determining which requirements are binding versus advisory, and ensuring that new specifications are correctly integrated into the authority chain.

This v1.1 update inserts the six Applied Sciences Extension Pack specifications into the authority chain and adds domain-specific override rules for biomedical, infrastructure, habitat, and knowledge-graph domains.

---

## Tier Structure

### Tier 0 — Constitutional Anchors

These documents define GAIA's fundamental operating boundaries. All other documents must be interpreted in their light. No lower-tier document may contradict a Tier 0 anchor.

| Document | Status |
|----------|--------|
| GAIA Open-Source Governance Framework v1.0 | Active |
| GAIA Product Boundary Spec | Expected baseline artifact — not yet in working corpus |
| GAIA Scope Matrix | Expected baseline artifact — not yet in working corpus |
| GAIA Boundary Compliance Header Standard | Expected baseline artifact — not yet in working corpus |
| Gaian v1 Architecture Spec | Expected baseline artifact — not yet in working corpus |
| ATLAS v1 Scope Note Patch Template | Expected baseline artifact — not yet in working corpus |

> **Note:** Documents marked "Expected baseline artifact" are recognized as constitutional companions in this index. When physically created, they automatically assume Tier 0 authority without requiring a further index update.

---

### Tier 1 — Binding Policy and Safety

These documents establish non-negotiable requirements. No deployment, feature, or implementation choice may violate a Tier 1 document.

| Document | Domain | Location |
|----------|--------|----------|
| GAIA Safety-Critical Systems Policy v1.0 | All safety-relevant systems | `docs/specs/safety/` |
| GAIA Biomedical Interface and Biosafety Spec v1.0 | Biomedical, biosecurity | `docs/specs/biomedical/` |
| GAIA Secure Compute and Verification Spec v1.0 | Compute, supply chain, crypto | `docs/specs/secure-compute/` |
| GAIA Contract Enforcement Framework v1.0 | Cross-system contracts | *(existing corpus)* |
| GAIA Inter-Core Contract Enforcement System v1.0 | Core-to-core contracts | *(existing corpus)* |

---

### Tier 2 — Architecture and Engineering Standards

These documents define how GAIA is built. They are binding for engineering decisions but may be adapted through the RFC process where technically necessary.

| Document | Domain | Location |
|----------|--------|----------|
| GAIA Repository Architecture and Engineering Systems v1.0 | All repos | *(existing corpus)* |
| GAIA Applied Sciences Knowledge Graph Spec v1.0 | SOPHIA / knowledge layer | `docs/specs/knowledge-graph/` |
| GAIA Infrastructure Digital Twin Spec v1.0 | URBS / TERRA / AQUA | `docs/specs/digital-twin/` |
| GAIA Habitat and Food Systems Intelligence Spec v1.0 | TERRA / VITA / URBS | `docs/specs/habitat/` |

---

### Tier 3 — Audit, Credibility, and Operational Standards

These documents define verification, auditability, and deployment operations. They are binding for any externally-facing or safety-relevant deployment.

| Document | Domain | Location |
|----------|--------|----------|
| GAIA Independent Auditability and Credibility Framework v1.0 | All systems | *(existing corpus)* |
| GAIA Production Deployment and Operations v1.0 | All deployments | *(existing corpus)* |
| GAIA Real-World Integration Standards v1.0 | External integrations | *(existing corpus)* |

---

### Tier 4 — Implementation Guidance

These documents provide non-binding guidance, patterns, and reference implementations. They may be followed or adapted at the implementer's discretion within the constraints of Tiers 0–3.

- Engineering RFCs
- Core-specific design guides
- SDK documentation
- Deployment runbooks
- Research proposals

---

## Conflict Resolution Rules

1. Higher-tier documents always outrank lower-tier documents.
2. Within the same tier, the Safety-Critical Systems Policy and Biomedical Spec outrank all other Tier 1 documents in their respective domains.
3. Tier 0 documents that are currently "expected baseline artifacts" shall be treated as if present and binding at Tier 0. When a conflict exists between an expected artifact's declared scope and any existing document, the Engineering Council shall resolve it.
4. Domain-specific specs (Tier 2) may impose stricter requirements than Tier 2 general architecture standards in their own domain. They may not relax Tier 1 requirements.
5. Any document that cannot be placed in this index must be treated as Tier 4 guidance until formally classified.

---

## Domain Override Rules

### Biomedical Domain
Within any system touching clinical data, patient safety, biosurveillance, or biological research:
- The Biomedical Interface and Biosafety Spec v1.0 is the primary domain authority.
- The Safety-Critical Systems Policy applies concurrently for any B2+ capability class.
- No Tier 2 or Tier 4 document may authorize biomedical actuation or relaxed biosafety constraints.

### Infrastructure and Digital Twin Domain
Within any system modeling or influencing physical infrastructure:
- The Infrastructure Digital Twin Spec v1.0 is the primary domain authority for twin architecture.
- The Safety-Critical Systems Policy governs all S2+ actuation and operational modes.
- Twin outputs must disclose synchronization class and quality index per the Digital Twin Spec.

### Habitat and Food Systems Domain
Within any system providing habitat, food, soil, or livability intelligence:
- The Habitat and Food Systems Intelligence Spec v1.0 is the primary domain authority.
- All outputs must expose uncertainty and locality dependence.
- Justice and access metrics are mandatory system performance indicators, not optional enhancements.

### Knowledge Graph Domain
Within SOPHIA and all systems contributing to or consuming the knowledge graph:
- The Applied Sciences Knowledge Graph Spec v1.0 is the primary domain authority.
- No core may silently redefine shared ontology classes without the RFC process defined in that spec.
- Evidence tier metadata must accompany all externally-facing knowledge claims.

---

## GUARDIAN Enforcement Role

GUARDIAN is the runtime enforcement authority for this index. GUARDIAN SHALL:

- maintain a live registry mapping all active GAIA subsystems to their applicable tier documents;
- block deployments that lack required Tier 1 compliance evidence;
- alert human operators when a conflict between tier documents is detected;
- sign all graph release manifests per the Knowledge Graph Spec;
- never be disabled, paused, or bypassed without Governance Council authorization.

---

## Index Maintenance

This index SHALL be reviewed:
- when any new canonical specification is adopted;
- when a Tier 0 expected baseline artifact is physically created;
- annually as a minimum;
- immediately following any Tier 1 policy violation or safety incident.

The next planned update is **GAIA Governance Index v1.2**, which will incorporate the GAIA Master Implementation Roadmap and Product Boundary Update once those documents are created.

---

## Change Log

| Version | Date | Change Summary |
|---------|------|----------------|
| v1.0 | Prior | Initial governance index |
| v1.1 | 2026-03-14 | Added six Applied Sciences Extension Pack specs; defined domain override rules; added Tier 0 expected baseline artifacts; added GUARDIAN enforcement role |
