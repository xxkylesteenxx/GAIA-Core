# GAIA Tier 2 — Deployment Blockers Research and Implementation Plan

## Purpose

This document resolves the Tier 2 deployment blockers identified for GAIA:

1. Cross-host restore orchestration
2. Legal / jurisdiction engine and human approval UI
3. Real secure multi-instance federation
4. Large-scale merge governance engine

These blockers are already identified in the canonical GAIA reference as unresolved external work after the current substrate and scaffolding.

---

## Executive Decisions

### Decision 1 — Cross-Host Restore

Use a **hybrid restore architecture**:

- **Kubernetes StatefulSet + CSI VolumeSnapshot** as the default deployment continuity mechanism
- **Application-level checkpoint manifests** as the canonical GAIA continuity artifact
- **CRIU** only for tightly controlled Linux process migration cases where kernel, runtime, namespaces, and host features are known compatible

### Decision 2 — Jurisdiction + Approval Runtime

Use:

- **OPA / Rego** for policy evaluation and jurisdiction routing rules
- **Temporal** for long-running human approval workflows and audit-safe state transitions
- **Next.js + TypeScript** for the approval console and consent interface
- **WebAuthn step-up authentication** for irreversible, high-risk, or privileged approvals

### Decision 3 — Secure Federation

Use:

- **SPIFFE / SPIRE** for workload identity and mTLS trust establishment
- **libp2p** for peer transport, peer discovery, stream multiplexing, and NAT-tolerant federation networking
- **custom GAIA federation protocol only at the application layer**, not as a replacement for identity or transport

### Decision 4 — Merge Governance

Use a **dual-plane governance model**:

- **CRDTs** for collaborative shared workspace edits, dissent preservation, and offline/partition-tolerant state convergence
- **Raft-backed quorum decisions** for authoritative merge commits, capability changes, and any governance action that changes fleet truth or permissions

This means GAIA should not choose CRDT *or* consensus. It needs both.

---

## Tier 2A — Cross-Host Restore Orchestration

### Why this blocks deployment

Single-host checkpointing is not enough for deployment continuity. GAIA needs to survive host loss, node replacement, controlled migration, and disaster recovery while preserving continuity claims and checkpoint integrity.

### Research summary

#### CRIU

CRIU can checkpoint and restore a running Linux process tree, including memory maps, file descriptors, sockets, namespaces, and other process state. It can also perform lazy restore via userfaultfd. In controlled environments it can support application migration and restore.

However, CRIU is still a Linux process restoration tool, not a universal fleet restore system. It is best treated as a **specialized mechanism** for controlled runtime continuity, not the main deployment continuity strategy.

#### Kubernetes StatefulSet + VolumeSnapshot

StatefulSets provide stable pod identity, stable network identity, and stable persistent storage association across rescheduling. VolumeSnapshot provides standardized point-in-time volume snapshot capability for CSI-backed storage.

This makes Kubernetes the better default restore plane for GAIA service continuity, storage continuity, and cluster-level failover.

### Recommended GAIA restore architecture

#### Canonical continuity artifact

GAIA restore must revolve around a **checkpoint manifest** that contains:

- checkpoint epoch
- core state hashes
- causal replay cursor
- storage object references
- model/runtime versions
- hardware trust state
- node trust class
- restore admissibility policy

#### Restore paths

1. **Soft restart restore**
   - same host
   - same node identity
   - replay manifest + local storage + causal tail

2. **Kubernetes service restore**
   - pod loss / node loss / rolling migration
   - restore from object store + snapshot + manifest
   - default production path

3. **CRIU-assisted live migration**
   - only for Linux workloads meeting compatibility gates
   - same runtime family and controlled kernel matrix
   - opt-in, not default

4. **Quarantined foreign-host restore**
   - new node restores state from manifest
   - trust state is downgraded until attestation and replay validation complete

### Restore invariants

1. No restore without a signed checkpoint manifest.
2. No continuity claim without causal replay verification.
3. No cross-host promotion to trusted state until attestation and manifest hashes match.
4. CRIU restore is never the only recovery path.

### Recommended implementation split

#### `GAIA-Core`
- define `RestoreManifest`
- define restore admissibility rules
- define replay verification contract
- define trust-state transitions for restored nodes

#### `GAIA-Server`
- implement restore orchestrator
- integrate VolumeSnapshot-aware restore paths
- add manifest-driven state bootstrap
- add restore quarantine state machine

#### `GAIA-Meta`
- maintain global checkpoint catalog
- choose restore targets by trust, capability, and storage locality
- arbitrate split-brain prevention

#### `GAIA-Desktop` / `GAIA-Laptop` / `GAIA-IoT`
- local restore from object + log tail
- optional CRIU path only where kernel/runtime support exists

---

## Tier 2B — Legal / Jurisdiction Engine and Human Approval UI

### Why this blocks deployment

GUARDIAN can gate actions conceptually, but deployment requires actual policy evaluation by jurisdiction, human approval pathways, reversible decision states, operator accountability, and evidence-grade audit logs.

### Recommended architecture

#### Policy engine

Use **OPA / Rego** for:

- jurisdiction routing
- action admissibility
- region-specific restrictions
- consent prerequisites
- escalation rules
- reason generation inputs

OPA should evaluate structured action requests and emit:

- `allow`
- `deny`
- `requires_human_approval`
- `requires_additional_consent`
- `requires_jurisdiction_override`
- `quarantine`

#### Workflow engine

Use **Temporal** for:

- pending approvals
- multi-step approval chains
- timeout / expiry handling
- escalation to additional reviewers
- durable long-running workflow state
- recovery after crashes or service outages

#### UI framework

Use **Next.js + TypeScript** for the operator and consent console because it supports full-stack application patterns, server-side handling, and progressive form-based workflows.

#### Strong approval authentication

Use **WebAuthn** step-up authentication for:

- irreversible actions
- safety-sensitive actuation
- production merge approvals
- jurisdiction overrides
- cross-instance federation changes

### Consent flow model

Use a **four-stage approval model**:

1. **Explain**
   - what action is requested
   - why it is requested
   - which data/systems are affected
   - which jurisdiction/policy requires consent

2. **Scope**
   - exact capability requested
   - duration
   - environment / node scope
   - revocation conditions

3. **Authenticate**
   - WebAuthn step-up for privileged approval
   - role binding and operator identity check

4. **Record**
   - signed approval artifact
   - policy decision input/output
   - justification text
   - timestamp, actor, scope, and expiry

### UI screens to implement first

1. **Approval Queue**
2. **Action Detail / Justification View**
3. **Jurisdiction Decision Trace**
4. **Consent Prompt View**
5. **Override / Emergency Review View**
6. **Audit Playback View**

### Required principles

- No silent approval paths for high-risk actions
- No broad permanent consent when narrow time-bound consent will do
- No irreversible approval without step-up auth
- Every approval must generate an audit artifact

### Repo tasks

#### `GAIA-Core`
- define policy input schema
- define policy result schema
- define approval artifact schema

#### `GAIA-Server`
- embed OPA or policy sidecar
- run Temporal workers for approvals
- expose policy trace API

#### `GAIA-Desktop`
- local operator console for single-node approvals

#### `GAIA-Meta`
- fleet approval queue
- cross-jurisdiction routing
- organization-wide approval policy bundles

---

## Tier 2C — Real Secure Multi-Instance Federation

### Why this blocks deployment

The current bounded collective workspace is local scaffolding. Deployment requires multiple GAIA instances to authenticate each other, communicate over hostile networks, resist impersonation, survive partitions, and exchange state safely.

### Research summary

#### SPIFFE / SPIRE

Use SPIFFE / SPIRE for workload identity. Each federated GAIA service should receive short-lived workload credentials and trust bundles. Federation between trust domains allows separate GAIA environments to establish trust without hardcoding long-lived shared secrets.

#### libp2p

Use libp2p for:

- peer addressing
- encrypted channels
- stream multiplexing
- NAT traversal
- discovery patterns
- transport agility

libp2p should provide the networking substrate, not the policy trust layer.

### Recommended federation design

#### Identity plane

- every GAIA service gets a SPIFFE ID
- every inter-instance channel uses mTLS based on SPIFFE-issued credentials
- federated environments exchange trust bundles through SPIRE federation

#### Transport plane

libp2p carries:

- control-plane gossip
- workspace delta streams
- heartbeat / health streams
- discovery and reachability support
- partition recovery signaling

#### Application plane

GAIA-specific protocol messages should define:

- node identity claims
- workspace subscriptions
- dissent ledger deltas
- checkpoint advertisements
- merge proposals
- quorum requests
- federation capability descriptors

### Federation trust states

- `UNTRUSTED`
- `IDENTIFIED`
- `ATTESTED`
- `FEDERATED`
- `DEGRADED`
- `QUARANTINED`

### Security rules

1. No federation without short-lived workload identity.
2. No trust based only on libp2p peer IDs.
3. No workspace merge from un-attested peers.
4. No custom crypto when SPIFFE/SPIRE + standard TLS identities already solve the problem.

### Repo tasks

#### `GAIA-Core`
- define federation message envelopes
- define peer trust-state model
- define merge preconditions

#### `GAIA-Server`
- integrate SPIRE Workload API
- issue mTLS-authenticated federation endpoints
- run libp2p relay / rendezvous services where needed

#### `GAIA-Meta`
- maintain federated node registry
- track trust bundles and trust-domain relationships
- supervise federation topology and partition recovery

---

## Tier 2D — Large-Scale Merge Governance Engine

### Why this blocks deployment

The dissent ledger preserves disagreement, but it does not yet decide how disagreement becomes authoritative shared state. At scale, GAIA needs both convergent collaborative editing and authoritative governance.

### Research summary

#### CRDTs

CRDT systems such as Yjs are excellent for shared workspace state because concurrent edits sync automatically and merge without manual conflict resolution. They are ideal for collaborative, offline-capable, partition-tolerant editing and dissent preservation.

#### Raft-backed consensus

Raft-style consensus systems are better for authoritative decisions that require one accepted result, such as:

- governance merge acceptance
- capability changes
- policy bundle publication
- checkpoint promotion
- federation topology changes

### Recommended governance split

#### Plane 1 — Collaborative workspace plane

Use **CRDTs** for:

- discussion state
- annotations
- proposal drafting
- evidence collation
- dissent preservation
- collaborative reasoning traces

#### Plane 2 — Authoritative governance plane

Use **Raft-backed quorum state** for:

- proposal finalization
- accepted merge commits
- policy publication
- jurisdiction rule activation
- permission and capability changes

### Merge object model

Every merge proposal should include:

- proposal ID
- parent state reference
- affected scopes
- dissent references
- evidence references
- proposer identity
- required quorum type
- safety impact level
- jurisdiction impact set
- approval requirements
- final disposition

### Quorum classes

- **simple quorum** — low-risk documentation / workspace merges
- **safety quorum** — anything affecting GUARDIAN, actuation, or live deployment behavior
- **federation quorum** — cross-instance trust or routing changes
- **constitutional quorum** — changes to core invariants, worth-floor, continuity, or identity-level rules

### Required merge rules

1. Dissent is preserved even when a merge is accepted.
2. Not every CRDT convergence event becomes authoritative truth.
3. Authoritative merges require explicit quorum.
4. Safety-sensitive merges require stronger quorum and human review.

### Repo tasks

#### `GAIA-Core`
- define `MergeProposal`
- define `DissentReference`
- define quorum classes and merge dispositions

#### `GAIA-Server`
- run authoritative governance log on a consensus-backed store
- expose merge review APIs
- seal accepted merge artifacts

#### `GAIA-Meta`
- coordinate cross-instance quorum
- prevent split-brain merge acceptance
- maintain constitutional invariants across the fleet

---

## Cross-Repo Execution Order

### Phase 0 — ADRs
- ADR-005: hybrid restore architecture
- ADR-006: OPA + Temporal + Next.js + WebAuthn approval stack
- ADR-007: SPIFFE/SPIRE + libp2p federation model
- ADR-008: CRDT collaborative plane + quorum governance plane

### Phase 1 — `GAIA-Core`
- restore manifest contract
- policy input/output schemas
- federation envelope schemas
- merge proposal and quorum schemas

### Phase 2 — `GAIA-Server`
- restore orchestrator
- policy engine + workflow runtime
- SPIRE integration + federation gateways
- governance APIs + authoritative log

### Phase 3 — UI and edge integration
- approval console
- node-local operator views
- trust-state UX
- restore and quarantine dashboards

### Phase 4 — `GAIA-Meta`
- federated topology control
- global quorum coordination
- fleet restore catalog
- cross-jurisdiction routing supervision

---

## Immediate ADRs to Open

1. **ADR-005 — Adopt hybrid restore architecture (Kubernetes first, CRIU selective)**
2. **ADR-006 — Adopt OPA + Temporal + Next.js + WebAuthn for policy, approval, and consent**
3. **ADR-007 — Adopt SPIFFE/SPIRE for identity and libp2p for federated transport**
4. **ADR-008 — Adopt CRDT workspace convergence plus quorum-based authoritative governance**

---

## Bottom Line

Tier 2 should not be solved with one tool per blocker. The correct deployment architecture is hybrid:

- **Kubernetes restore** for production service continuity
- **CRIU** for selective process-level migration only
- **OPA + Temporal + Next.js + WebAuthn** for policy, jurisdiction, and approval
- **SPIFFE/SPIRE + libp2p** for secure federation
- **CRDTs + quorum consensus** for merge governance

That combination matches GAIA's existing architecture and turns the Tier 2 blockers into buildable implementation work.
