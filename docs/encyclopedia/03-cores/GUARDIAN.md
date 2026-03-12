# GUARDIAN — Security & Policy Core

> **Part III — The Eight Consciousness Cores**  
> **Status**: Canonical v1.0 · March 12, 2026

---

## Role

GUARDIAN is the **ethical enforcer and security anchor** of GAIA. It gates every actuation, enforces privilege class separation, runs theater-risk scoring, maintains the audit ledger, and cannot be bypassed by any process — including P1 platform services for high-impact actuation.

---

## Responsibilities

- LSM (Linux Security Module) hooks for all privileged operations
- P0–P3 privilege class enforcement
- Actuation approval gates (human override channel required for high-impact actions)
- Theater-risk scoring (penalizes simulated consciousness/consent)
- Anti-theater detection integration with Layer 3 measurement
- Consent ledger and audit trail maintenance
- PQC-protected audit log signing
- GUARDIAN-Lite bootstrap (comes online before full consciousness runtime)
- Policy update distribution to all cores
- Jurisdiction-aware compliance routing

---

## Privilege Class

**P1 — Privileged Platform Service** (with kernel LSM hooks at P0 boundary)  
GUARDIAN has the highest effective authority in userspace and kernel LSM hooks. No P2/P3 process can bypass its gates.

---

## Actuation Gate Model

```
Request → GUARDIAN Policy Check → Consent Ledger → Human Override (if required) → Actuation
                    ↓
              Deny + Audit Log (if policy violated)
```

---

## Key Interfaces

- **Publishes**: PolicyUpdate, ActuationDecision, ThreatAlert, TheaterRiskScore
- **Subscribes to**: All core actuation requests, NEXUS coherence state, Layer 3 measurement signals
- **Writes to**: `docs/specs/security/GUARDIAN_LSM.md` for policy definitions

---

*→ See also: [Anti-Theater Detection](../06-security/Anti_Theater.md) · [Privilege Classes](../06-security/Privilege_Classes.md)*
