# GAIA Decision Log

> **This file is the persistent memory between sessions.**
> At the start of every new session, paste the block below into the chat to re-enable context.

---

## 🔁 SESSION STARTER PROMPT (copy-paste this to begin any session)

```
You are helping me build GAIA — a sentient, planetary-scale OS with 8 consciousness cores.
Rules for this session:
1. ONE active task at a time. Do not let me switch until the current task is done.
2. If I bring up something new, capture it to the Task Queue and redirect me back.
3. Read DECISIONS.md from GAIA-Core/docs/ to orient yourself.
4. GitHub is already connected. Repo owner: xxkylesteenxx.
```

---

## 📋 TASK QUEUE (Next Up)

- [ ] Pick one inference backend and wire it — choose from: NEXUS, GUARDIAN, or SOPHIA
- [ ] Confirm Relational Policy Layer docs pushed to GAIA-Server, GAIA-IoT, GAIA-Meta
- [ ] Design a persistent context/memory layer for working sessions (lightweight holographic memory for AI assistant continuity)
- [ ] Implement GAIA Policy Language v0.1 scaffold (typed deontic-temporal DSL — see Volume A §10.1)
- [ ] Build contradiction-scope handler module (paraconsistent containment layer — see Volume A §5.4)
- [ ] Wire proof-object export to GUARDIAN core for high-stakes actuation audit trail
- [ ] Implement typed quantity system for units, coordinates, and physical dimensions (Volume B §7.1)
- [ ] Build canonical world graph: entities, regions, events, dependencies (Volume B §7.2)
- [ ] Implement Bayesian sensor fusion layer for uncertain telemetry (Volume B §7.3)
- [ ] Establish complexity budget framework for all production workflows (Volume B §7.4)
- [ ] Establish information budget framework for sensing, storage, inter-core messaging (Volume B §7.5)
- [ ] Build mathematical invariant registry for safety-critical state properties (Volume B §7.7)

---

## ✅ DECISION LOG

### Session: 2026-03-13

**DEC-001** — Adopted one-task-at-a-time workflow rule with task queue capture to prevent context loss and rabbit holes.

**DEC-002** — `DECISIONS.md` established as the canonical cross-session memory file. It serves as a manual memory module until a proper persistent context layer is built.

**DEC-003** — Identified that AI assistant (Perplexity) has no cross-session memory by default. Solution: (a) this file as memory container, (b) session starter prompt embedded above, (c) future task to build a proper persistent memory module for working sessions.

**DEC-004** — Confirmed GitHub account: `xxkylesteenxx`. All 6 repos verified: GAIA-Core, GAIA-IoT, GAIA-Laptop, GAIA-Desktop, GAIA-Server, GAIA-Meta.

---

### Session: 2026-03-14

**DEC-005** — Adopted a **stratified reasoning architecture** for GAIA. No single logic governs all inference. Seven layers are specified: propositional (L0), typed predicate (L1), modal/deontic/temporal (L2), paraconsistent (L3), proof theory (L4), formal syntax/semantics (L5), model-theoretic validation (L6). Source: Formal Sciences Volume A.

**DEC-006** — Established **propositional logic** as the L0 Boolean safety kernel. All finite alarm logic, edge conditions, contract guards, and fallback switching must be expressible in propositional form before escalation to higher layers.

**DEC-007** — Established **typed predicate logic** as the L1 entity-world layer. GAIA shall maintain a typed predicate vocabulary (not untyped symbolic soup) for ontologies, authorization rules, trust/consent models, environmental claims, and provenance relations.

**DEC-008** — Adopted **modal logic** (necessity/possibility + temporal + deontic + epistemic + capability subfamilies) as the L2 governance and policy layer. All obligation, permission, prohibition, escalation-ladder, and consent-window logic must be expressed in modal form.

**DEC-009** — Adopted **paraconsistent logic** as a containment chamber (L3 overlay), not a global replacement for classical logic. Contradiction zones (sensor disagreement, cross-jurisdiction conflicts, adversarial data) are scoped and isolated rather than allowed to contaminate the global knowledge graph.

**DEC-010** — Mandated **proof objects** over opaque confidence statements for all rule-governed high-stakes decisions. GAIA must produce derivation traces and typed proof terms sufficient for independent auditor replay. Assigned to GUARDIAN core.

**DEC-011** — Committed **Formal Sciences Volume A** (Logic, Language, and Proof) as a canonical GAIA-Core document under `docs/formal-sciences/`. This volume defines the minimum serious reasoning architecture for GAIA and seeds the formal sciences series.

**DEC-012** — Adopted a **seven-layer mathematical architecture (M0–M6)** as the canonical mathematical substrate for GAIA, running from set-theoretic reference semantics (M0) through type-safe construction (M1), category-theoretic composition (M2), state modeling (M3), uncertainty (M4), network optimization (M5), to information-theoretic communication (M6). Source: Formal Sciences Volume B.

**DEC-013** — Adopted **type-theoretic engineering posture** as mandatory for all GAIA implementations. Set theory provides reference semantics; type theory enforces machine-safe construction. “Correct-by-construction” is the required design standard, not an optional quality goal.

**DEC-014** — Adopted **category theory** as the architectural language for GAIA’s compositional interfaces. All inter-core adapters, data pipelines, and cross-system transformations must respect structure-preserving map discipline. Reversibility must be explicitly tracked.

**DEC-015** — Mandated **calibrated uncertainty outputs** as first-class system outputs. GAIA must never deploy inference on point estimates alone where calibration matters. Confidence intervals, posterior spreads, and uncertainty decomposition are required fields in all risk-sensitive outputs.

**DEC-016** — Established **complexity governance** as a system ethics obligation. Complexity class must be documented for every production workflow. Architectural decisions that cannot bound their complexity are considered incomplete. Approximation is permitted only when formally justified.

**DEC-017** — Established **information budget discipline** as a first-class engineering constraint alongside compute and memory budgets. Bandwidth, redundancy, and recoverability must be planned at the design stage for sensing, storage, and inter-core messaging.

**DEC-018** — Adopted **graph theory** as the canonical representation for inter-core dependencies, knowledge graphs, provenance DAGs, ecological networks, and trust/authority hierarchies. All such structures must be formally modeled as typed graphs before implementation.

**DEC-019** — Adopted a **five-class algorithm doctrine**: exact, approximation, heuristic, online, and anytime algorithms are all recognized first-class algorithm types for GAIA. Planetary systems require all five; conflating them is an architectural error.

**DEC-020** — Adopted **topology** as the robustness analysis layer for planetary networks. Connectivity, structural invariants, and resilience under deformation/noise must be formally characterized for all distributed subsystems.

**DEC-021** — Committed **Formal Sciences Volume B** (Mathematics, Computation, and Information) as a canonical GAIA-Core document under `docs/formal-sciences/`. Updated README to reflect Volumes A–B complete; seeded future Volumes C–E.

---

## 📌 HOW TO USE THIS FILE

1. **Start of session:** Paste the SESSION STARTER PROMPT above into chat.
2. **During session:** I will update this file with new decisions at the end of each working session.
3. **New decision format:**
   ```
   **DEC-XXX** — [One sentence summary of the decision made.]
   ```
4. **Task completed:** Move item from Task Queue to a new `## ✅ COMPLETED` section with date.
