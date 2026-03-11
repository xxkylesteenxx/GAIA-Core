---
v1 Boundary Compliance: IN SCOPE
Relevant v1 Sections: 16
Post-v1 Tag: NO
Post-v1 Milestone: NA
Scope Matrix Tier: MUST SHIP
---

# GAIA Governance Index v1.0

**Status:** Canonical 
**Purpose:** Single entry point for the GAIA v1 governance chain 
**Rule:** All GAIA technical work is governed by the documents listed here, in the authority order shown.

---

## Authority Order

| Priority | Document | Role | Version |
|----------|----------|------|---------|
| 1 | GAIA-v1-Product-Boundary-Spec-v1.1.md | Defines what v1 is and is not; governs all scope | v1.1 |
| 2 | GAIA-v1-Scope-Matrix-v1.0.md | Defines Must/Should/May/Deferred tiers | v1.0 |
| 3 | GAIA-Boundary-Compliance-Header-Standard-v1.0.md | Mandatory front matter for all specs | v1.0 |
| 4 | GAIA-Gaian-v1-Architecture-Spec-v1.0.md | First post-boundary engineering target | v1.0 |
| 5 | GAIA-ATLAS-v1-Scope-Note-Patch-Standard-Template.md | Remediation standard for environmental corpus | v1.0 |

**No technical spec may expand scope beyond the Product Boundary Spec without a formal revision to that document.** Tier changes in the Scope Matrix require a version bump and boundary spec owner sign-off.

---

## Pending Actions (as of governance baseline adoption)

### Immediate
- [ ] Add three PR checklist items per Boundary Compliance Header Standard §5 (all 6 repos)
- [ ] Add REMEDIATION PENDING notice to five unpatched domain/ATLAS specs:
  - AERO domain spec
  - TERRA domain spec
  - AQUA domain spec
  - VITA domain spec
  - ATLAS interoperability/publishing specs
- [ ] Queue Product Boundary Spec v1.1 — add Trust success criterion to §14 (already included in this commit)

### Then
- [ ] Apply ATLAS v1 Scope Note Patch in order: AERO → TERRA → AQUA → VITA → Interoperability specs
- [ ] Begin spec remediation using compliance header for all major existing specs

---

## Invariants

These rules do not change without a formal governance revision:

1. No spec may claim v1 scope without a compliant Boundary Compliance Header.
2. No Deferred item may enter a v1 milestone without boundary spec owner sign-off.
3. No ATLAS domain spec may be used as a v1 implementation target without its v1 Scope Note patch applied.
4. No public or internal GAIA framing may use language prohibited by Product Boundary Spec §13.
5. The priority order of §16 governs all future spec prioritization: OS → Gaian → ATLAS → Hardening → Ecosystem.

---

## What the Governance Baseline Closes

**Before this baseline, GAIA had:**
- Strong technical architecture specs
- No product boundary document
- No scope enforcement mechanism
- No mandatory compliance front matter
- No explicit deferral list
- No Gaian engineering target

**After this baseline, GAIA has:**
- A normative product boundary (Product Boundary Spec)
- An explicit tiered scope (Scope Matrix)
- Mandatory per-spec compliance declaration (Header Standard)
- A self-enforcing ATLAS corpus repair mechanism (Scope Note Patch Template)
- The first flagship experience engineering target (Gaian v1 Architecture Spec)

The boundary is now operational, not aspirational.
