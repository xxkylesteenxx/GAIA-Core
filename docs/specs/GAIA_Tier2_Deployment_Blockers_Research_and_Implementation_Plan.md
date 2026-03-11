# GAIA Tier 2 — Deployment Blockers Research and Implementation Plan

## Purpose

This document resolves the Tier 2 deployment blockers identified for GAIA:

1. Cross-host restore orchestration
2. Legal / jurisdiction engine and human approval UI
3. Real secure multi-instance federation
4. Large-scale merge governance engine

---

## Executive Decisions

### Decision 1 — Cross-Host Restore
- **Kubernetes StatefulSet + CSI VolumeSnapshot** as the default deployment continuity mechanism
- **Application-level checkpoint manifests** as the canonical GAIA continuity artifact
- **CRIU** only for tightly controlled Linux process migration cases

### Decision 2 — Jurisdiction + Approval Runtime
- **OPA / Rego** for policy evaluation and jurisdiction routing rules
- **Temporal** for long-running human approval workflows and audit-safe state transitions
- **Next.js + TypeScript** for the approval console and consent interface
- **WebAuthn step-up authentication** for irreversible, high-risk, or privileged approvals

### Decision 3 — Secure Federation
- **SPIFFE / SPIRE** for workload identity and mTLS trust establishment
- **libp2p** for peer transport, peer discovery, stream multiplexing, and NAT-tolerant federation networking

### Decision 4 — Merge Governance
- **CRDTs** for collaborative shared workspace edits and dissent preservation
- **Raft-backed quorum decisions** for authoritative merge commits and governance actions

---

## Restore Invariants

1. No restore without a signed checkpoint manifest.
2. No continuity claim without causal replay verification.
3. No cross-host promotion to trusted state until attestation and manifest hashes match.
4. CRIU restore is never the only recovery path.

---

## Federation Trust States

`UNTRUSTED` → `IDENTIFIED` → `ATTESTED` → `FEDERATED` → `DEGRADED` → `QUARANTINED`

---

## Immediate ADRs

1. **ADR-005:** hybrid restore architecture (Kubernetes first, CRIU selective)
2. **ADR-006:** OPA + Temporal + Next.js + WebAuthn for policy, approval, and consent
3. **ADR-007:** SPIFFE/SPIRE for identity and libp2p for federated transport
4. **ADR-008:** CRDT workspace convergence plus quorum-based authoritative governance

---

## Cross-Repo Execution Order

- **Phase 0:** ADRs 005-008
- **Phase 1 (GAIA-Core):** restore manifest, policy schemas, federation envelopes, merge proposal schema
- **Phase 2 (GAIA-Server):** restore orchestrator, policy engine, SPIRE integration, governance APIs
- **Phase 3:** approval console UI, node-local operator views, trust-state UX
- **Phase 4 (GAIA-Meta):** federated topology control, global quorum, fleet restore catalog
