---
v1 Boundary Compliance: IN SCOPE
Relevant v1 Sections: 7, 12, 13, 16
Post-v1 Tag: NO
Post-v1 Milestone: NA
Scope Matrix Tier: MUST SHIP
---

# GAIA ATLAS v1 Scope Note Patch Standard Template

**Status:** Canonical remediation template 
**Applies to:** All ATLAS-adjacent environmental domain specs (TERRA, AQUA, AERO, VITA) and all ATLAS interoperability/publishing specs 
**Application order:** AERO → TERRA → AQUA → VITA → Interoperability/Publishing specs 
**Rule:** No environmental domain spec may serve as a v1 implementation target until its v1 Scope Note patch has been applied and committed.

---

## 1. Header Block

Insert the following at the top of each target document, immediately after the document title, status, and author fields:

```
---
v1 Boundary Compliance: PARTIALLY IN SCOPE
Relevant v1 Sections: 7, 12, 13, 16
Post-v1 Tag: YES
Post-v1 Milestone: ATLAS v2
Scope Matrix Tier: MIXED
---
```

---

## 2. v1 Scope Note Section

Insert the following section immediately before the first requirements section in each target document. Complete the bracketed fields for each domain.

### For AERO

**v1 In Scope:**
- One live or near-live atmospheric observation source (e.g., NOAA GFS or ERA5 subset)
- One STAC or OGC endpoint publishing AERO observation metadata
- One AERO domain summary surface for the Gaian ATLAS-aware mode
- Brian2 CPU-baseline neuromorphic prototype (May Ship, not v1 blocking)

**Post-v1:**
- Full atmospheric column coverage at planetary scale
- Multi-model ensemble fusion
- Loihi 2 hardware neuromorphic deployment
- Domain-specific operator workflow automation

**Deferred from this document by GAIA v1 Product Boundary Spec §7 and §12:**
- Complete live simulation of Earth’s atmosphere
- Cross-domain coherence and synthesis at ATLAS v2 scale

### For TERRA

**v1 In Scope:**
- One live land or geophysical data source (e.g., USGS or Copernicus Land subset)
- One STAC endpoint publishing TERRA observation metadata
- Contribution to one domain dashboard (May Ship)

**Post-v1:**
- Full geospatial coverage across all land surface types
- Complete geophysical monitoring integration

**Deferred by §7 and §12:** Complete planetary land simulation twin.

### For AQUA

**v1 In Scope:**
- One hydrological data source (e.g., USGS stream gauge or Copernicus Marine subset)
- Standards-compliant metadata publication for selected sources

**Post-v1:** Full operational AQUA coverage.

**Deferred by §7 and §12:** Complete ocean/hydrological simulation twin.

### For VITA

**v1 In Scope:**
- Biodiversity data contribution to ATLAS discovery surface only (e.g., GBIF or iNaturalist selected dataset)

**Post-v1:** Full VITA biological/ecological domain coverage.

**Deferred by §7 and §12:** No operational VITA simulation in v1; discovery surface only.

---

## 3. REMEDIATION PENDING Notice

Until a domain spec has been patched per this template, it must carry the following notice at the top of its document:

```
> ⚠️ **REMEDIATION PENDING** — This document has not yet received its v1 Scope Note patch per
> `GAIA-ATLAS-v1-Scope-Note-Patch-Standard-Template.md`. It must not be used as a v1 implementation
> target until remediated.
```

---

## 4. Application Order and Rationale

| Order | Document | Rationale |
|-------|----------|----------|
| 1 | AERO domain spec | Neuromorphic pilot domain first; likely ATLAS dashboard source |
| 2 | TERRA domain spec | Land/geophysical sources most accessible for STAC publication |
| 3 | AQUA domain spec | Well-standardized sources; lower v1 priority than AERO/TERRA |
| 4 | VITA domain spec | v1 contribution is discovery-surface only; simplest patch |
| 5 | ATLAS interoperability/publishing specs | Must not imply full planetary coverage even in infra framing |

---

## 5. Application Checklist

For each target document, confirm before committing:

- [ ] Boundary Compliance Header block inserted (§1 of this template)
- [ ] v1 Scope Note section inserted before first requirements section (§2)
- [ ] v1 In Scope subsection completed for this specific domain
- [ ] Post-v1 subsection completed
- [ ] Deferred subsection cross-references Product Boundary Spec sections
- [ ] Document framing language reviewed against §13 naming and framing rules
- [ ] PR checklist items confirmed per Boundary Compliance Header Standard §5
- [ ] REMEDIATION PENDING notice removed after patch is applied
