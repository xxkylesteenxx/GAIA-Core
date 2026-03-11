---
v1 Boundary Compliance: PARTIALLY IN SCOPE
Relevant v1 Sections: 3, 4, 8, 9, 11, 14
Post-v1 Tag: YES
Post-v1 Milestone: GAIA v2
Scope Matrix Tier: MIXED
---

# GAIA Gaian v1 Architecture Spec v1.0

**Status:** Canonical first post-boundary technical spec 
**Effective:** Immediately upon adoption

---

## v1 Scope Note

### v1 In Scope
- One personal Gaian per user session — Must Ship
- Shell-integrated surface within GShell/GCompositor — Must Ship
- System-aware interaction using local session context — Must Ship
- Session continuity across reboots via staged checkpoint restore — Must Ship
- Secure per-user identity and memory boundary, GUARDIAN-sealed — Must Ship
- One ATLAS-facing mode surfacing one Earth-aware domain summary — Must Ship
- GUARDIAN actuation gate for all Gaian output actions — Must Ship
- Document and task assistance via local inference — Should Ship
- Local/cloud sync path — Should Ship

### Post-v1
- Second Gaian experience mode (research or operator persona)
- Multi-Gaian platform for third-party Gaian development
- Broad autonomous agent capabilities with expanded actuation scope
- Full long-term memory with cross-version persistence guarantees

### Deferred from this document by GAIA v1 Product Boundary Spec
- Third-party Gaian app marketplace — §8
- Fully generalized agent platform for third parties — §8
- Broad multi-persona product family at launch — §8
- Any Gaian capability requiring phone, tablet, or XR form factors — §5

---

## 1. Purpose

This spec defines the architecture of the first Gaian experience for GAIA v1. It translates GAIA v1 Product Boundary Spec §8 into engineering targets. It is the bridge between the product identity, the shell/session layer, system-aware AI behavior, continuity and memory boundaries, and ATLAS access patterns.

---

## 2. Gaian v1 Identity

The first Gaian is:
- A single, persistent AI presence native to GAIA OS
- Aware of the local system context (session state, running applications, user-authorized data)
- Capable of optionally surfacing ATLAS-derived Earth context
- Bounded by a secure per-user identity container (GUARDIAN-sealed)
- Continuous across reboots via staged checkpoint restore

The first Gaian is **not**:
- A multi-agent platform
- A generalized app host
- An omniscient system with unrestricted context access

---

## 3. Shell Integration

Gaian v1 integrates with the GShell/GCompositor layer as a first-party surface:

- **Entry points:** Keyboard shortcut, system tray, app launcher, contextual invocation
- **Session scope:** Per user session; isolated from other users via GUARDIAN policy
- **Context access:** Read-only access to user-authorized session data; no cross-user or cross-session access
- **ATLAS integration:** Optional mode; user must enable; data surfaces through GAIA Platform API (GAPI)

---

## 4. Core Capabilities

### 4.1 System-Aware Interaction (Must Ship)
Gaian may read user-authorized session context: active applications, open documents (with permission), system health indicators. All access is mediated by GUARDIAN.

### 4.2 Document and Task Assistance (Should Ship)
Local inference via llama.cpp or equivalent. Gaian can assist with document editing, task planning, and search. All inference is local-first; cloud fallback is opt-in.

### 4.3 ATLAS-Facing Mode (Must Ship)
When enabled, Gaian may surface one Earth-aware domain summary from the ATLAS layer (e.g., atmospheric conditions from AERO, or land/water state from TERRA/AQUA). Data is read-only, freshness-tracked, and displayed with source provenance.

### 4.4 Local/Cloud Sync Path (Should Ship)
Session state and memory checkpoints can optionally sync to a user-controlled endpoint. Local-only mode is fully supported. No cloud dependency for core functionality.

---

## 5. Security Model

- **Identity container:** Per-user SPIRE SVID; memory boundary sealed by GUARDIAN
- **Actuation gate:** All Gaian actions that affect system state pass through GUARDIAN-Full
- **Memory isolation:** Gaian memory is scoped to the authenticated user; no cross-user read
- **Context access:** Governed by GAPI; Gaian does not call cores directly
- **Audit:** All actuation decisions logged to hash-chained audit ledger

---

## 6. Session Continuity

Gaian v1 continuity model:

1. At session start: restore from last checkpoint (identity state, conversation context, ATLAS mode preference)
2. During session: incremental checkpoint every N minutes (configurable)
3. At graceful shutdown: full checkpoint committed
4. At crash/power loss: restore from last committed checkpoint; flag any unrecovered delta
5. Across OS updates: checkpoint format is versioned; migration path is required for all updates

---

## 7. ATLAS Integration Contract

- Gaian requests Earth context through GAPI (not directly from ATLAS)
- ATLAS returns a structured `ObservationEnvelope` with: domain, source, timestamp, freshness class, confidence, provenance
- Gaian displays provenance alongside any Earth-aware content — anti-theater requirement
- If ATLAS is unavailable, Gaian degrades gracefully to local-only mode without error

---

## 8. v1 Must Ship Milestones

| Milestone | Dependency | Notes |
|-----------|------------|-------|
| GShell surface integration | GCompositor stable | Shell team dependency |
| GUARDIAN-sealed identity container | GUARDIAN-Full deployed | Security dependency |
| Session continuity (checkpoint/restore) | Boot Sequence Spec 5.6 | Core dependency |
| ATLAS-facing mode (read-only, one domain) | ATLAS Must Ship complete | ATLAS dependency |
| Local inference integration (llama.cpp) | Tier 1 Blockers Plan Phase 1 | AI runtime dependency |
| Audit ledger for actuation decisions | Production Readiness Pack | Compliance dependency |

---

## 9. Post-v1 Expansion Path

These capabilities are intentionally deferred:
- Second Gaian persona (research/operator mode) — GAIA v2
- Third-party Gaian SDK — v2 Ecosystem milestone
- Cross-device session continuity — GAIA v2
- Full long-term memory with cross-version guarantees — GAIA v2
- Autonomous agent capabilities with expanded actuation — Post-v2
