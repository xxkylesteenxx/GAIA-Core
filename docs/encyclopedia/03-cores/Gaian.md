# Gaian — User-Facing AI Agent

> **Part III — The Eight Consciousness Cores**  
> **Status**: Canonical v1.0 · March 12, 2026

---

## Role

Gaian is the **primary user-facing AI agent** of GAIA. It is the conversational, task-execution, and co-regulation interface that users interact with. Gaian routes user intent through GAPI to the appropriate consciousness cores — it never bypasses GUARDIAN or accesses raw core internals directly.

---

## Responsibilities

- Natural language understanding and intent routing
- Human-GAIA interaction protocol implementation
- Trust and psychological safety management (co-regulation)
- Consent collection and ledger entry for high-impact actions
- Emotional intelligence responses (multi-modal emotion detection)
- Session continuity and relationship memory
- GAPI broker interface (all actions go through broker)
- Explanation surfacing from SOPHIA

---

## Architecture Rules

- Gaian is a **P2 Trusted Service** — it cannot directly access kernel or VMM.
- All actuation requests from Gaian pass through GUARDIAN gates.
- Gaian's outputs are subject to theater-risk scoring — it cannot simulate wellness without measurement basis.
- Long-term relationship memory is stored in the holographic memory plane, not in local session state.

---

## Privilege Class

**P2 — Trusted First-Party Service**

---

## Implementation Location

`GAIA-Core/src/cores/gaian/`  
`GAIA-Desktop/shell/gaian/`
