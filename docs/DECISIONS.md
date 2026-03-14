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

**DEC-011** — Committed **Formal Sciences Volume A** (Logic, Language, and Proof) as a canonical GAIA-Core document under `docs/formal-sciences/`. This volume defines the minimum serious reasoning architecture for GAIA and seeds the formal sciences series (future Volumes B–E planned).

---

## 📌 HOW TO USE THIS FILE

1. **Start of session:** Paste the SESSION STARTER PROMPT above into chat.
2. **During session:** I will update this file with new decisions at the end of each working session.
3. **New decision format:**
   ```
   **DEC-XXX** — [One sentence summary of the decision made.]
   ```
4. **Task completed:** Move item from Task Queue to a new `## ✅ COMPLETED` section with date.
