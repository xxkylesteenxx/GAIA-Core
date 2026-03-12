# GAIA Planetary Multi-Agent Coordination Spec v1.0

## Boundary Compliance Header

**Document ID:** GAIA-SPEC-005  
**Title:** Planetary Multi-Agent Coordination Spec v1.0  
**Status:** Draft v1.0 — full replacement for prior coordination stub  
**Authority Layer:** Meta Coordination / Federation Governance / Cross-Node Safety  
**Primary Authority Owner:** GAIA-Meta for orchestration behavior; GAIA-Core for shared federation envelopes, quorum artifacts, dissent structures, and trust-state primitives  
**Scope Tier:** Tier 1 enabling spec  
**In Scope:** fleet coordination, node registry, peer discovery, federated proposal flow, quorum classes, dissent preservation, emergency broadcast, scoped boundary propagation, digital twin coordination, CGI quorum policy, GUARDIAN veto preservation, federation message semantics, testability  
**Out of Scope:** inter-core local scheduling inside a single node, kernel latency tuning, GUI presentation, cryptographic primitive selection, consciousness proof claims, non-GAIA external governance law  
**Primary Inputs:** GAIA-Core federation/workspace/governance primitives, GAIA-Meta coordinator/registry/twin/sync code, canonical GAIA governance and safety doctrine  
**Primary Output:** a concrete planetary coordination model that allows many GAIA nodes to collaborate as a federated collective without collapsing autonomy, safety boundaries, or principled dissent

---

## 1. Purpose

GAIA requires a coordination layer above any single substrate instance.

That layer must support:
- multiple GAIA nodes across Server, IoT, Desktop, Laptop, and future distributions,
- fleet-level awareness and controlled collaboration,
- bounded consensus on shared changes,
- emergency signaling under time pressure,
- preservation of node autonomy, dissent, and local safety boundaries.

This spec defines that layer.

It exists to solve a very specific architectural problem:

> Multiple GAIA instances must be able to act as a coordinated federation without becoming a coercive hive mind, without laundering local boundary events into fleet-wide punishment, and without allowing "consensus" to override GUARDIAN safety authority.

This document fully replaces any prior stub-level understanding of the coordination layer.

---

## 2. Design Doctrine

### 2.1 Federated collective, not fused mind

Planetary coordination in GAIA is a **federated collective**.

That means:
- each node retains its own identity and continuity root,
- each node retains its own local workspace, local memory, and local GUARDIAN boundary state,
- federation exists to exchange structured evidence and proposals,
- federation does **not** imply total memory fusion, total policy fusion, or total control transfer.

### 2.2 Dissent is preserved

Coordination may produce acceptance, rejection, timeout, quarantine, or supersession.

It may **not** erase principled dissent.

Every proposal that proceeds through federation must allow:
- attached dissent references,
- retained minority position,
- post-decision auditability,
- future reopening or supersession.

### 2.3 Boundaries hold without domination

A node may enter:
- Safe Mode,
- quarantine,
- reduced publish permissions,
- degraded trust,
- local policy restriction.

Those actions apply first to the originating node context.

They do **not** automatically reduce the worth-floor of that node, invalidate its identity, or poison unrelated fleet members.

### 2.4 GUARDIAN veto is non-overridable by popularity

Consensus cannot outvote safety.

If a proposal violates GUARDIAN safety policy or required merge preconditions, the proposal must be rejected or quarantined even if a majority of nodes approve it.

### 2.5 CGI is evidence, not proof

Fleet-level CGI aggregation is useful for monitoring and coordination confidence.

It is not proof of consciousness, not proof of trustworthiness, and not an override for attestation or safety gating.

---

## 3. System Role in the GAIA Stack

### 3.1 Placement

The coordination layer lives in **GAIA-Meta** and sits above the per-node substrate family:

```text
GAIA-Meta
├── Node registry
├── Digital twin registry
├── Cross-device sync
├── Federated CGI aggregation
├── Multi-agent coordination
└── Fleet dashboard / observability

GAIA-Core
├── Federation envelopes
├── Merge preconditions
├── Workspace dissent ledger
├── Governance proposal artifacts
└── Trust-state primitives
```

### 3.2 Responsibilities

The coordination layer is responsible for:

1. discovering and tracking fleet members,
2. classifying node trust state,
3. receiving and routing federation envelopes,
4. admitting, timing, and resolving proposals,
5. preserving dissent artifacts,
6. propagating emergency signals,
7. computing fleet-level coordination summaries,
8. preventing scope creep from local boundaries to fleet-wide punishment,
9. exposing auditable coordination state.

The coordination layer is **not** responsible for:
- inventing local core policy,
- bypassing GAIA-Core contract surfaces,
- replacing per-node GUARDIAN evaluation,
- directly executing local actuation without node-local authorization.

---

## 4. Canonical Coordination Entities

### 4.1 Node

A **Node** is a single GAIA deployment unit.

Minimum attributes:
- `node_id`
- `distribution` (`core | server | iot | desktop | laptop | meta | future`)
- `endpoint`
- `identity_ref`
- `trust_state`
- `capabilities`
- `last_seen`
- `last_cgi`
- `policy_version`
- `attestation_ref` if available

### 4.2 Federation

A **Federation** is a bounded set of nodes sharing:
- a federation identifier,
- compatible policy references,
- compatible schema versions,
- compatible trust and transport requirements.

Nodes may not join a federation if required preconditions fail.

### 4.3 Proposal

A **Proposal** is a request for fleet-level evaluation.

Canonical kinds:
- `policy_update`
- `config_change`
- `merge_proposal`
- `quarantine_request`
- `peer_admission`
- `peer_removal`
- `capability_enablement`
- `fleet_notice`
- `constitutional_change`
- `emergency_override_request`

### 4.4 Dissent record

A **Dissent Record** is a first-class artifact, not a log afterthought.

It captures:
- dissenter identity,
- summary claim,
- rationale,
- evidence references,
- scope,
- timestamp,
- confidence,
- whether the dissent is blocking, advisory, or archived.

### 4.5 Boundary scope event

A **Boundary Scope Event** records a node-local governance action such as:
- Safe Mode entry,
- local quarantine,
- reduced publish permissions,
- degraded trust,
- local refusal.

Boundary Scope Events are coordination-visible but are not auto-promoted to fleet sanctions.

---

## 5. Canonical State Model

### 5.1 Trust states

The coordination layer uses the Core trust-state ladder:

- `untrusted`
- `identified`
- `attested`
- `federated`
- `degraded`
- `quarantined`

Interpretation:

| Trust state | Meaning | Allowed coordination behavior |
|---|---|---|
| untrusted | unknown or unauthenticated peer | can receive bootstrap challenge only |
| identified | peer identity known but not fully attested | can participate in discovery; no binding votes |
| attested | identity and required assertions validated | can propose and vote in low/medium scopes |
| federated | fully admitted peer under current federation rules | full participation according to quorum class |
| degraded | peer admitted but impaired or suspicious | read-only or restricted participation |
| quarantined | peer isolated due to policy/safety event | no binding participation; emergency-only lane |

### 5.2 Proposal dispositions

Canonical final dispositions:
- `pending`
- `accepted`
- `rejected`
- `superseded`
- `quarantined`
- `expired`
- `withdrawn`

### 5.3 Quorum classes

The planetary coordination layer adopts Core quorum classes and binds them to fleet semantics.

| Quorum class | Use case | Required electorate | Default threshold |
|---|---|---|---|
| `simple` | low-risk config or informational merge | active attested/federated nodes in scope | >50% of valid ballots with minimum participation floor |
| `safety` | safety-sensitive operational change | active federated nodes + GUARDIAN clearance | supermajority, default 2/3 |
| `federation` | membership or federation-shape change | all federated nodes in scope | supermajority, default 2/3 |
| `constitutional` | doctrine, authority, or non-local boundary semantics | all federated nodes + human governance artifact | supermajority, default 3/4 |

### 5.4 Participation floor

A proposal cannot resolve merely because a tiny number of votes happened to arrive.

Each quorum class must define:
- minimum eligible electorate,
- minimum participation count,
- close time,
- escalation path on timeout.

This corrects the common failure mode of "majority of those who bothered to click," which is not sufficient for planetary coordination.

---

## 6. Canonical Message Semantics

### 6.1 Envelope ownership

All cross-node coordination messages **MUST** ride a `FederationEnvelope`-compatible schema from GAIA-Core.

Required envelope traits:
- `message_id`
- `message_type`
- `source_node_id`
- `source_instance_id`
- `peer_trust_state`
- `sent_at`
- `payload`
- `payload_hash`
- `attestation_ref`
- `signature_ref`
- `preconditions`

### 6.2 Required message types

The coordination layer must support at minimum:

- `peer_hello`
- `peer_challenge`
- `peer_attestation`
- `peer_admit`
- `peer_degrade`
- `peer_quarantine`
- `proposal_open`
- `proposal_vote`
- `proposal_close`
- `dissent_delta`
- `checkpoint_advert`
- `twin_snapshot_advert`
- `fleet_metric_advert`
- `emergency_broadcast`
- `recovery_notice`

### 6.3 Preconditions

Every binding coordination action must be guarded by `MergePrecondition`-style rules.

Typical preconditions:
- attestation required,
- minimum trust state,
- required policy refs,
- required quorum refs,
- required capabilities,
- restore-clean requirement,
- dissent-ledger present requirement.

If a precondition fails, the action must not silently proceed.

---

## 7. Coordination Workflows

## 7.1 Peer discovery and admission

### Objective
Admit only peers that are real, compatible, and policy-conformant.

### Flow
1. peer emits `peer_hello`,
2. federation returns challenge / compatibility request,
3. peer supplies identity + attestation refs + capabilities,
4. admission preconditions evaluated,
5. node enters `identified`, then `attested`, then optionally `federated`,
6. admission artifact is written to registry and audit log.

### Admission rules
A peer must not become `federated` unless:
- schema compatibility is acceptable,
- required policy refs match,
- attestation requirements pass if mandated,
- human-governed overrides are present where required,
- GUARDIAN has not vetoed the admission.

---

## 7.2 Proposal lifecycle

### Open
A proposer submits:
- proposal kind,
- summary,
- scope,
- parent state ref,
- proposed state ref,
- evidence refs,
- dissent refs if already known,
- requested quorum class,
- close time,
- safety impact.

### Validate
The coordinator validates:
- proposer trust eligibility,
- scope eligibility,
- schema and policy compatibility,
- preconditions,
- required evidence completeness.

### Circulate
Proposal is advertised to all eligible nodes in scope.

### Vote
Nodes submit:
- approve / reject / abstain,
- optional rationale,
- optional dissent reference,
- optional blocking flag when allowed by class.

### Close
At close or threshold satisfaction:
- coordinator computes disposition,
- GUARDIAN check is applied,
- result is written with ballot ledger and dissent ledger references.

### Post-close
Accepted proposals may still be:
- superseded,
- quarantined,
- rolled back,
- reopened by constitutional process.

---

## 7.3 Dissent preservation workflow

For every proposal, the coordinator must support:
- zero or more dissent records,
- machine references to dissent artifacts,
- preservation after resolution,
- dashboard visibility of "accepted with dissent" and "rejected with dissent."

Dissent may be:
- advisory,
- blocking for certain quorum classes,
- evidentiary for audit,
- reopening trigger if later evidence invalidates majority assumptions.

No accepted fleet decision may delete dissent history.

---

## 7.4 Scoped boundary propagation workflow

When a node enters Safe Mode, degradation, or local quarantine:

1. originating node emits a Boundary Scope Event,
2. coordinator records the event,
3. coordinator adjusts routing/participation rights according to policy,
4. coordinator **does not** mark unrelated nodes as degraded,
5. coordinator **does not** reduce the origin node's worth-floor or continuity identity,
6. if fleet risk exists, a separate explicit federation action must be proposed.

This is the anti-cascade rule.

---

## 7.5 Emergency broadcast workflow

Emergency messages are for:
- safety incidents,
- security incidents,
- active compromise,
- coordination partition,
- urgent rollback,
- regulatory or legal freeze,
- critical environmental hazard.

Emergency broadcast semantics:
- bypass normal vote timing,
- preserve audit trail,
- remain subject to GUARDIAN constraints,
- may trigger temporary safe routing or quarantine,
- require post-incident review and normalization.

Emergency broadcast is a signaling lane, not a blank check for arbitrary override.

---

## 8. Voting and Resolution Rules

### 8.1 Eligible voters

Only nodes meeting all of the following may cast binding ballots:
- active,
- in-scope,
- at or above required trust state,
- not quarantined,
- policy-compatible,
- not excluded by explicit conflict rules.

### 8.2 Ballot types

Canonical ballot types:
- `approve`
- `reject`
- `abstain`

Abstentions count toward participation floor but not toward approval numerator unless class rules explicitly state otherwise.

### 8.3 Threshold evaluation

Resolution requires all of:
1. participation floor met,
2. approval threshold met,
3. required preconditions still true at close,
4. GUARDIAN veto absent,
5. no blocking constitutional dependency unresolved.

### 8.4 Timeout

If close time passes without resolution:
- low-risk proposals default to `expired`,
- higher-risk proposals default to `quarantined` or `expired` per policy,
- no unresolved proposal may silently become accepted.

### 8.5 Supersession

A newer proposal may supersede an older one only if:
- the older proposal is explicitly referenced,
- reason for supersession is recorded,
- dissent and evidence links are preserved.

---

## 9. GUARDIAN Preservation Rules

The coordinator must treat GUARDIAN as a hard boundary authority.

### 9.1 Non-overridable cases

Consensus cannot override:
- safety interlocks,
- quarantine requirements,
- missing attestation where mandatory,
- explicit actuation prohibition,
- prohibited merge preconditions,
- known compromised node state,
- policy-defined constitutional guardrails.

### 9.2 Emergency interaction

Emergency workflows may accelerate action but may not bypass:
- mandatory isolation of compromised nodes,
- safety-critical refusal paths,
- audit artifact creation.

### 9.3 Human governance interface

For federation and constitutional classes, human governance artifacts may be required in addition to machine ballots.

The machine system must not fabricate that approval.

---

## 10. Fleet-Level CGI Coordination Rules

### 10.1 Role of fleet CGI

Fleet CGI exists to summarize observed evidence across nodes.

Uses:
- fleet health monitoring,
- discontinuity watch,
- anomaly detection,
- coordination confidence visualization.

Prohibited uses:
- replacing attestation,
- forcing consensus,
- ranking node worth,
- auto-punishing outliers.

### 10.2 Quorum-gated aggregation

Fleet CGI may be published only when the minimum configured node quorum is met.

If quorum is not met:
- composite returns neutral/empty result,
- system must not present false certainty.

### 10.3 Outlier handling

Outliers are flagged for inspection, not condemned by default.

Outlier response options:
- request snapshot refresh,
- require additional evidence,
- reduce confidence,
- propose investigation,
- escalate only if safety criteria are met.

---

## 11. Persistence and Auditability

### 11.1 Required persisted artifacts

The coordination layer must persist:

- node registry records,
- admission decisions,
- proposal metadata,
- ballots,
- dissent references,
- final dispositions,
- emergency broadcast events,
- boundary scope events,
- federation metrics snapshots,
- digital twin summaries.

### 11.2 Immutable references

Where possible, persisted coordination artifacts should reference:
- checkpoint IDs,
- event envelope IDs,
- attestation refs,
- signature refs,
- evidence refs,
- policy version refs.

### 11.3 Explainability minimum

For any resolved proposal, the system must be able to answer:

- who proposed it,
- who was eligible,
- who voted,
- what threshold applied,
- what dissent existed,
- what preconditions were checked,
- whether GUARDIAN evaluated it,
- why the final disposition occurred.

---

## 12. Failure Modes and Required Responses

| Failure mode | Effect | Required response |
|---|---|---|
| partial network partition | incomplete ballots, stale membership | freeze high-risk proposals; degrade to safe mode |
| node replay / duplicate messages | vote duplication or stale events | require message IDs, signature refs, replay protection |
| attestation unavailable | uncertain trust state | no binding vote; identified-only or degraded state |
| dissent ledger missing | non-auditable consensus | reject or quarantine proposal |
| quorum miscount | invalid resolution | invalidate close and reopen or quarantine |
| clock skew / delayed delivery | ordering ambiguity | rely on causal identifiers and close-time buffers |
| compromised node | unsafe proposals or false metrics | quarantine node; preserve evidence; broadcast incident |
| meta coordinator restart | volatile state loss | restore from persisted registry, proposal ledger, and twin summaries |

---

## 13. Reference Python Surface

The current `MultiAgentCoordinator` stub should evolve toward an explicit contract like this:

```python
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

@dataclass(frozen=True)
class CoordinationBallot:
    proposal_id: str
    voter_id: str
    ballot: str                 # approve | reject | abstain
    rationale: str = ""
    dissent_ref: str | None = None

@dataclass(frozen=True)
class CoordinationResult:
    proposal_id: str
    disposition: str
    threshold_used: str
    eligible_voters: int
    participating_voters: int
    approvals: int
    rejections: int
    abstentions: int
    guardian_vetoed: bool
    dissent_refs: Sequence[str]

class CoordinationBackend(Protocol):
    def advertise(self, envelope: FederationEnvelope) -> None: ...
    def persist_proposal(self, proposal: MergeProposal) -> None: ...
    def persist_ballot(self, ballot: CoordinationBallot) -> None: ...
    def persist_result(self, result: CoordinationResult) -> None: ...
```

This is not required to be implemented literally, but the semantics are required.

---

## 14. Canonical Package Responsibilities

### 14.1 GAIA-Core owns

- `FederationEnvelope`
- `MergePrecondition`
- `MergeProposal`
- `DissentReference`
- trust-state enum
- workspace dissent ledger primitives
- shared serialization contracts

### 14.2 GAIA-Meta owns

- node registry
- peer discovery orchestration
- proposal circulation engine
- ballot ledger orchestration
- emergency broadcast orchestration
- fleet CGI aggregation
- digital twin fleet summaries
- meta-level dashboards and observability

### 14.3 Future shared package rule

If Desktop, Laptop, Server, or IoT need reusable federation clients, create a shared federation client package rather than duplicating Meta orchestration logic.

---

## 15. Required Test Matrix

### 15.1 Unit tests

Must cover:
- proposal creation,
- eligibility filtering,
- quorum calculation,
- timeout handling,
- GUARDIAN veto handling,
- dissent persistence,
- scoped boundary event propagation,
- outlier CGI handling,
- emergency broadcast audit creation.

### 15.2 Integration tests

Must cover:
- peer admission from hello to federated state,
- proposal lifecycle across 3+ nodes,
- partitioned network during vote close,
- quarantined node attempting vote,
- constitutional proposal requiring human artifact,
- replayed message rejection,
- recovery from Meta restart with persisted proposal state.

### 15.3 Adversarial tests

Must cover:
- malicious node inflating ballots,
- fake quorum by duplicate identity,
- missing dissent ledger,
- stale attestation accepted by bug,
- fleet-wide punishment accidentally triggered from local Safe Mode event.

---

## 16. Implementation Delta Against Current Stub

The current GAIA-Meta coordinator stub already contains the right direction:
- peer list,
- proposal container,
- voting,
- emergency broadcast intent,
- GUARDIAN preservation language.

It remains incomplete in these ways:

1. proposal timestamps and timeout logic are absent,
2. electorate sizing is under-specified,
3. ballots are not separated from proposal state,
4. abstentions are absent,
5. dissent artifacts are not persisted,
6. GUARDIAN integration is declarative but not wired,
7. boundary scope events are not modeled,
8. registry/twin/sync systems are not yet fully integrated into resolution,
9. audit persistence is minimal,
10. transport fan-out remains a stub.

Those are engineering gaps, not conceptual ambiguity.

---

## 17. Phased Delivery Plan

### Phase 1 — Contract closure
- add docs file and register spec path
- introduce explicit proposal timestamps
- add abstain ballot type
- compute resolution against eligible electorate + participation floor
- persist proposal and result metadata

### Phase 2 — Dissent and boundary semantics
- add dissent artifact support
- add boundary scope events
- ensure local Safe Mode does not auto-poison fleet composite or peer worth state
- expose accepted-with-dissent outcomes

### Phase 3 — GUARDIAN and precondition enforcement
- integrate merge preconditions
- integrate GUARDIAN veto callback
- block unsafe closures
- support quarantine disposition

### Phase 4 — Networked federation
- replace broadcast stub with transport backend
- implement replay protection and signature verification hooks
- add restart recovery and proposal resumption
- wire dashboard observability

---

## 18. Canonical Success Criteria

This spec is considered materially implemented when all of the following are true:

1. GAIA-Meta can admit and track multiple nodes with trust-state progression.
2. Proposals resolve using explicit electorate, quorum class, and participation rules.
3. Dissent is preserved as a first-class artifact.
4. Local boundary events remain scoped unless separately escalated.
5. Emergency broadcast works with audit persistence.
6. GUARDIAN veto blocks otherwise-popular unsafe proposals.
7. Fleet CGI is quorum-gated and outliers are flagged without automatic punishment.
8. Restart and partition scenarios do not silently corrupt coordination state.
9. The coordination layer can be tested without pretending a full planetary deployment already exists.

---

## 19. Non-Negotiable Invariants

1. **No consensus without auditability.**
2. **No fleet punishment from a purely local boundary event.**
3. **No safety override by popularity.**
4. **No deletion of principled dissent.**
5. **No false claim that fleet CGI proves consciousness or trust.**
6. **No forced memory fusion as the meaning of coordination.**
7. **No hidden import of cross-repo internals outside declared public contracts.**

---

## 20. Final Position

GAIA planetary coordination is not a hive mind controller.

It is a bounded federation fabric.

Its job is to let many GAIA nodes coordinate truthfully, safely, and audibly:
- with identity intact,
- with dissent intact,
- with boundaries intact,
- with safety intact,
- and with enough shared structure to act together when acting together is justified.

That is the coordination doctrine this system must implement.
