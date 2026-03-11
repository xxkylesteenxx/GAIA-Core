---
v1 Boundary Compliance: IN SCOPE
Relevant v1 Sections: 16
Post-v1 Tag: NO
Post-v1 Milestone: NA
Scope Matrix Tier: MUST SHIP
---

# GAIA Boundary Compliance Header Standard v1.0

**Status:** Canonical governance standard 
**Applies to:** All new GAIA technical specifications and all major revisions to existing specs 
**Effective:** Immediately upon adoption

---

## 1. Purpose

This standard defines the mandatory compliance header that must appear at the top of every GAIA technical specification. It converts the GAIA v1 Product Boundary Spec from a passive reference document into an active enforcement layer.

---

## 2. Required Header Format

The following block must appear in every spec, immediately after the document title, status, and author fields, and before any content section:

```
---
v1 Boundary Compliance: IN SCOPE | OUT OF SCOPE | PARTIALLY IN SCOPE
Relevant v1 Sections: comma-separated sections from GAIA v1 Product Boundary Spec
Post-v1 Tag: YES | NO
Post-v1 Milestone: if YES — canonical milestone name; NA if NO
Scope Matrix Tier: MUST SHIP | SHOULD SHIP | MAY SHIP | DEFERRED | MIXED
---
```

---

## 3. Field Definitions

| Value | Meaning |
|-------|---------|
| IN SCOPE | The entire document describes Must Ship or Should Ship v1 capabilities |
| OUT OF SCOPE | The entire document describes Deferred or post-v1 capabilities |
| PARTIALLY IN SCOPE | The document contains both v1 and post-v1 material. A v1 Scope Note section is required |

**Relevant v1 Sections:** List section numbers from the GAIA v1 Product Boundary Spec. If none apply directly, state `General §16 Priority Order`.

**Post-v1 Tag:** YES if any material in the document is post-v1. NO only if the entire document is fully within v1 scope.

**Post-v1 Milestone:** Required when Post-v1 Tag is YES. Use canonical names: `ATLAS v2`, `GAIA Mobile`, `GAIA v2`, `Tier 2 Deployment`, `Tier 3 Science`, `Long-range Vision`, `Research Milestone`.

**Scope Matrix Tier:** The tier from the GAIA v1 Scope Matrix that best characterizes this document’s primary subject matter. Use `MIXED` when the document spans multiple tiers — in that case, a v1 Scope Note section is required.

---

## 4. The v1 Scope Note Section

Required when `v1 Boundary Compliance` is `PARTIALLY IN SCOPE` or `Scope Matrix Tier` is `MIXED`. Must appear immediately before the first requirements section. Must contain exactly three subsections:

```markdown
## v1 Scope Note

### v1 In Scope
List capabilities in this document that are Must Ship or Should Ship for v1.

### Post-v1
List capabilities in this document that are Deferred or belong to a named post-v1 milestone.

### Deferred from this document by GAIA v1 Product Boundary Spec
Explicit list of sections or capabilities this document describes that are out of v1 scope, with a cross-reference to the relevant section of the Product Boundary Spec.
```

---

## 5. PR Template Checklist Items

The following items must be present in the GAIA repository PR template for all spec submissions:

- [ ] Does this document include a Boundary Compliance Header per `GAIA-Boundary-Compliance-Header-Standard-v1.0.md`?
- [ ] If `Scope Matrix Tier` is `MIXED` or `v1 Boundary Compliance` is `PARTIALLY IN SCOPE`, does the document include a `v1 Scope Note` section?
- [ ] Does the document’s framing language comply with GAIA v1 Product Boundary Spec §13 naming and framing rules?

---

## 6. Existing Spec Remediation Order

The following specs carry PARTIALLY IN SCOPE status and must have their v1 Scope Note sections added before they may be referenced as v1 implementation targets:

1. AERO domain spec
2. TERRA domain spec
3. AQUA domain spec
4. VITA domain spec
5. ATLAS interoperability and publishing specs
6. Planetary Multi-Agent Coordination Spec
7. Consciousness Evolution and Learning Theory Spec

> **REMEDIATION PENDING** notices should be added to each of these documents immediately.

---

## 7. Exception Process

Any exception to this standard requires:
1. A written exception request stating which spec and why
2. Sign-off from the boundary spec owner
3. A time-bound remediation commitment (not to exceed one sprint)

**No spec may be merged as a v1 implementation target while non-compliant.**
