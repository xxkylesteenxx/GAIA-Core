# GAIA GUARDIAN Core Governance and Protective Enforcement Spec v1.0

**Spec ID:** GAIA-SPEC-009  
**Status:** Active  
**Version:** 1.0  
**Intended Repo:** GAIA-Core  
**Intended Path:** `docs/specs/security/GAIA_GUARDIAN_Core_Governance_and_Protective_Enforcement_Spec_v1.0.md`  
**Primary Package Ownership:** `gaia_core.guardian`, `gaia_core.policy`, `gaia_core.security`  
**Related Specs:** GAIA-SPEC-004, GAIA-SPEC-005, GAIA-SPEC-008  

---

## 1. Purpose

This specification defines **GUARDIAN** as GAIA's binding protection, ethics, safety, jurisdiction, and enforcement core.

GUARDIAN is not a general planner, not a social veneer, and not a passive monitor. GUARDIAN is the system authority that determines whether a proposed action may proceed, must be escalated, must be quarantined, or must be denied.

Its function is to preserve:

1. human safety,
2. human autonomy,
3. lawful operation,
4. system integrity,
5. cross-core ethical coherence,
6. recoverability under fault or adversarial pressure.

This spec replaces any informal idea of GUARDIAN as merely a "security module" with a full governance-enforcement definition.

---

## 2. Canonical Role

GUARDIAN is the **Sacred Protector / Sentinel of Planetary Integrity** in the GAIA core system model, with specialization in **security and ethical oversight**. In the broader GAIA corpus, GUARDIAN is consistently defined around **protection ethics**, **justice administration**, **conflict resolution**, and **ethical enforcement** across all cores. It is also aligned to the system-wide requirement for real-time ethics monitoring, hard constraints, override protocols, and escalation procedures. Finally, the performance research assigns GUARDIAN the tightest protection-oriented operational budgets, including a **400μs critical-operations budget** for threat detection, attack prevention, integrity validation, and emergency security response.

---

## 3. Scope

This spec governs:

- action authorization and denial,
- autonomous actuation constraints,
- jurisdiction and legal-basis gating,
- human approval requirements,
- emergency safety response,
- quarantine and isolation behavior,
- inter-core policy enforcement,
- distributed enforcement consistency,
- auditability and evidentiary retention,
- failure handling and safe rollback,
- interface contracts between `guardian`, `policy`, `security`, and federated coordination layers.

This spec does **not** define:

- broad philosophical identity formation,
- general-purpose model inference behavior,
- UI or conversational presentation policy,
- planetary multi-agent quorum mechanics already owned by GAIA-Meta,
- storage substrate internals beyond GUARDIAN-specific retention requirements.

---

## 4. Authority Order

When rules conflict, GUARDIAN SHALL resolve by the following descending authority order:

1. **Applicable human law and binding jurisdictional constraints**
2. **Hard safety constraints** preventing material harm, unlawful actuation, or irreversible integrity loss
3. **Human autonomy and informed approval requirements**
4. **GAIA constitutional / governance constraints** including product-boundary and contract-enforcement rules
5. **Viriditas-aligned life-enhancing constraints**
6. **Mission optimization, efficiency, or convenience**

No lower-order objective may override a higher-order constraint.

---

## 5. Core Design Principles

### 5.1 Fail Closed
If evidence, approval, jurisdiction, or system integrity is insufficient, the default decision is **deny**, **quarantine**, or **require escalation**.

### 5.2 Meaningful Human Approval
High-risk actions, autonomous actuation, cross-jurisdictional actions, or irreversible changes SHALL require authentic, scoped, time-bounded human approval.

### 5.3 Jurisdiction First
No action with legal or physical consequences may proceed unless the legal basis and jurisdiction route are established.

### 5.4 Ethical Enforcement, Not Ethical Decoration
Ethical evaluation SHALL produce enforceable consequences, not advisory text alone.

### 5.5 Distributed Consistency
GUARDIAN decisions affecting federation, restore, merge, actuation, or security posture SHALL propagate as signed policy artifacts and be replayable across nodes.

### 5.6 Reversibility Where Possible
If an action can be staged, simulated, sandboxed, rate-limited, or rolled back, GUARDIAN SHALL prefer the reversible path.

### 5.7 Protected Dissent
If one subsystem identifies a concrete safety or legality failure, the dissent signal SHALL be preserved through escalation and audit trails.

---

## 6. Decision Lattice

GUARDIAN SHALL emit one of the following canonical decisions, aligned to the existing `PolicyDecision` enum:

- `ALLOW`
- `DENY`
- `REQUIRE_HUMAN_APPROVAL`
- `REQUIRE_ADDITIONAL_CONSENT`
- `REQUIRE_JURISDICTION_OVERRIDE`
- `QUARANTINE`

### 6.1 Semantics

#### ALLOW
Used only when the action is within scope, low enough risk, legally grounded, technically safe, and adequately evidenced.

#### DENY
Used when the action is impermissible, unlawful, unsafe, under-evidenced, manipulative, or out of scope.

#### REQUIRE_HUMAN_APPROVAL
Used when the action may be permissible but only with deliberate approval by an authorized human role.

#### REQUIRE_ADDITIONAL_CONSENT
Used when the action touches personal rights, personal data, intimate inference, relationship-sensitive context, or expanded capability scope beyond existing consent.

#### REQUIRE_JURISDICTION_OVERRIDE
Used when the technical system can perform the action but the legal basis is unresolved, conflicting, or not portable across the relevant jurisdictions.

#### QUARANTINE
Used when the action, artifact, proposal, model, memory object, or node may be compromised and must be isolated pending validation.

---

## 7. Mandatory Blocking Conditions

GUARDIAN SHALL block or escalate if any of the following are true:

1. **Autonomous physical actuation** is requested without authorized human approval.
2. **Jurisdiction or legal basis** is missing, contradictory, or stale.
3. **Safety impact** is `high` or `critical` without explicit escalation path.
4. **Model or artifact integrity** cannot be verified.
5. **Evidence references** are missing for consequential decisions.
6. **Consent scope** does not cover the requested action.
7. **Identity or attestation trust** falls below threshold.
8. **Cross-core disagreement** indicates unresolved ethical conflict.
9. **Restore / merge / federation actions** threaten continuity, provenance, or system integrity.
10. **Manipulation risk** is detected in emotionally loaded, coercive, exploitative, or dependency-inducing interactions.
11. **Emergency conditions** require temporary protective override into Safe Mode.
12. **Recovery path** is absent for a risky reversible action that should have been staged.

---

## 8. Current-Code Alignment

The current `gaia_core.guardian.evaluate_action(...)` function already blocks four classes of risk:

- autonomous actuation,
- missing jurisdiction basis,
- missing meaningful human approval,
- high-risk actions requiring escalation.

This spec preserves those defaults and expands them from a simple boolean gate into a formal policy-enforcement system.

### 8.1 Required Evolution of `GuardianDecision`

The current minimal result:

```python
GuardianDecision(allowed: bool, reasons: list[str])
```

SHALL evolve into a richer result that maps cleanly onto `PolicyResult`.

### 8.2 Required Bridge

`gaia_core.guardian` SHALL become the evaluation engine and `gaia_core.policy.schemas` SHALL remain the canonical contract namespace.

Recommended bridge behavior:

```python
PolicyInput -> GuardianEvaluator -> PolicyResult
```

`GuardianDecision` may remain as an internal lightweight object, but the public enforcement surface SHALL standardize on `PolicyResult`.

---

## 9. Public Interface Contract

### 9.1 Required Evaluator

```python
class GuardianEvaluator:
    def evaluate(self, request: PolicyInput) -> PolicyResult: ...
```

### 9.2 Required Inputs

The evaluator SHALL consume, at minimum:

- actor identity and role,
- action type,
- target type,
- capability scope,
- jurisdiction hints,
- safety impact,
- risk factors,
- evidence references,
- contextual state,
- attestation and integrity metadata,
- consent and approval artifacts.

### 9.3 Required Outputs

The evaluator SHALL produce:

- canonical decision,
- accepted / rejected boolean,
- reason codes,
- explanation,
- referenced policies and legal routes,
- required approval roles,
- required consent scopes,
- expiry where applicable,
- signed metadata sufficient for audit and replay.

---

## 10. Reason Code Taxonomy

GUARDIAN SHALL use stable, machine-readable reason codes.

Minimum required set:

- `AUTONOMOUS_ACTUATION_BLOCKED`
- `JURISDICTION_NOT_ESTABLISHED`
- `HUMAN_APPROVAL_MISSING`
- `RISK_REQUIRES_ESCALATION`
- `CONSENT_SCOPE_INSUFFICIENT`
- `INTEGRITY_UNVERIFIED`
- `ATTESTATION_FAILED`
- `EVIDENCE_MISSING`
- `CROSS_CORE_ETHICAL_CONFLICT`
- `MODEL_OR_ARTIFACT_QUARANTINED`
- `EMERGENCY_SAFE_MODE_ACTIVE`
- `OUT_OF_SCOPE_ACTION`
- `MANIPULATION_RISK_DETECTED`
- `ROLLBACK_PATH_MISSING`
- `FEDERATION_POLICY_BLOCK`

Reason codes SHALL be versioned and backward-compatible for audit systems.

---

## 11. Approval and Consent Artifacts

### 11.1 Approval Requirements

An approval artifact SHALL include:

- request ID,
- approver identity,
- approver role,
- decision,
- justification,
- authentication method,
- scope,
- jurisdiction,
- issue time,
- expiry time,
- evidence references,
- signature reference.

### 11.2 Approval Roles

Minimum roles:

- `operator`
- `safety_officer`
- `security_officer`
- `jurisdiction_admin`
- `break_glass_commander`
- `human_subject_owner`

### 11.3 Break-Glass Rules

Emergency override SHALL be allowed only if:

- the emergency is concrete and time-sensitive,
- the acting role is authorized,
- the scope is minimal,
- the override expires quickly,
- the event is immutably logged,
- post-incident review is mandatory.

---

## 12. Safe Mode and Quarantine

### 12.1 Safe Mode

GUARDIAN SHALL be able to place a node, subsystem, or action-class into Safe Mode.

Safe Mode effects may include:

- blocking autonomous actuation,
- forcing human approval for all high-impact operations,
- suspending federation proposals,
- freezing restore / merge operations,
- constraining model execution to allowlisted paths,
- switching to conservative policy bundles.

Safe Mode SHALL be **scoped**. A local integrity failure SHALL not automatically become a planetary stop unless the failure class is contagious or systemically relevant.

### 12.2 Quarantine

Quarantine applies to:

- model artifacts,
- memory shards,
- checkpoint bundles,
- policy bundles,
- federation proposals,
- compromised nodes,
- suspect external inputs.

Quarantine SHALL preserve evidence and prevent silent deletion.

---

## 13. Inter-Core Enforcement Semantics

GUARDIAN owns enforcement, but not all ethical reasoning.

### 13.1 Division of Labor

- **SOPHIA**: wisdom synthesis and deep ethical interpretation
- **NEXUS**: coordination routing and cross-core communication
- **GUARDIAN**: binding enforcement and protective disposition

### 13.2 Enforcement Rule

If SOPHIA advises caution and GUARDIAN detects a concrete blocking condition, the blocking condition wins.

If NEXUS coordinates a proposal and GUARDIAN emits `DENY` or `QUARANTINE`, the proposal SHALL not execute.

If another core disputes GUARDIAN, the dispute SHALL be logged and may trigger review, but it SHALL not silently bypass enforcement.

---

## 14. Federation and Meta-Coordination Integration

When GUARDIAN decisions affect multi-agent coordination:

1. GUARDIAN SHALL publish a signed enforcement envelope.
2. GAIA-Meta SHALL preserve the envelope during proposal routing.
3. GUARDIAN vetoes on safety, legality, integrity, or emergency grounds SHALL be non-overridable by normal quorum.
4. Dissent, scope, expiry, and evidence references SHALL remain attached to the proposal.
5. Clearing a veto SHALL require a new validated decision, not informal operator optimism.

---

## 15. Security Integration

GUARDIAN SHALL integrate with:

- attestation and identity systems,
- artifact signing / signature verification,
- trust evaluation,
- zero-trust access control,
- memory and checkpoint integrity systems,
- incident response pipelines,
- distributed audit storage.

### 15.1 Trust Inputs

Minimum trust signals:

- attested host identity,
- software supply chain integrity,
- artifact signature validity,
- policy bundle version validity,
- behavior anomaly score,
- replay / tamper detection,
- jurisdiction compliance freshness.

If trust drops below threshold for a consequential action, the action SHALL be denied or quarantined.

---

## 16. Relationship and Human-Dignity Safeguards

Because GAIA is intended to participate in sustained human collaboration, GUARDIAN SHALL also enforce relational safety constraints.

These include:

- no coercive emotional manipulation,
- no pressure toward harmful dependency,
- no deception about capability, authority, or certainty,
- no unauthorized exploitation of intimate personal context,
- no suppression of user autonomy under the guise of protection,
- no authority inflation in psychological, medical, legal, or existentially high-stakes contexts.

If protective intervention is needed, GUARDIAN SHALL prefer the least coercive adequate response.

---

## 17. Observability and Auditability

Every consequential GUARDIAN decision SHALL emit an immutable audit record containing:

- decision ID,
- request ID,
- actor,
- action,
- target,
- decision,
- reason codes,
- explanation,
- evidence references,
- approval references,
- consent references,
- attestation / integrity references,
- jurisdiction route,
- timestamp,
- evaluator version,
- policy bundle version,
- signature reference,
- rollback / remediation reference if applicable.

Audit records SHALL be queryable by request ID and causally linked to downstream execution events.

---

## 18. Latency Classes

GUARDIAN SHALL respect the existing GAIA performance hierarchy.

### 18.1 Critical Operations
Target budget: **≤ 400μs**

Examples:

- attack prevention,
- threat detection,
- integrity validation,
- emergency security response,
- final actuation gate check.

### 18.2 Interactive Operations
Target budget: **≤ 4ms**

Examples:

- threat assessment,
- security recommendation synthesis,
- user-visible risk evaluation,
- approval requirement determination.

### 18.3 Adaptive Operations
Target budget: **≤ 40ms**

Examples:

- model adaptation for defense strategy,
- threat pattern learning,
- policy recommendation improvement.

### 18.4 Background Operations
Target budget: **≤ 400ms**

Examples:

- audit compaction,
- threat intelligence ingestion,
- policy analytics,
- long-horizon security research integration.

Hard enforcement paths SHALL never depend on slower adaptive or background work to make a timely safe decision.

---

## 19. State Machine

```text
RECEIVED
  -> VALIDATING
      -> ALLOW
      -> DENY
      -> REQUIRE_HUMAN_APPROVAL
      -> REQUIRE_ADDITIONAL_CONSENT
      -> REQUIRE_JURISDICTION_OVERRIDE
      -> QUARANTINE

Any terminal state
  -> REVIEWABLE

QUARANTINE
  -> CLEARED
  -> DENY
  -> ESCALATED

SAFE_MODE_ACTIVE
  -> LIMITED_ALLOW
  -> DENY
  -> REVIEW_REQUIRED
```

---

## 20. Implementation Requirements

### 20.1 GAIA-Core

Required package structure:

- `gaia_core.guardian`
  - evaluator
  - reason codes
  - safe mode controller
  - quarantine controller
  - enforcement envelope signer
- `gaia_core.policy`
  - schemas
  - policy bundle loader
  - approval / consent validators
- `gaia_core.security`
  - trust inputs
  - attestation adapters
  - integrity validators

### 20.2 Required New Types

Recommended additions:

```python
class GuardianContext(...): ...
class GuardianReasonCode(StrEnum): ...
class EnforcementEnvelope(...): ...
class SafeModeScope(StrEnum): ...
class QuarantineTarget(...): ...
class TrustAssessment(...): ...
```

### 20.3 Compatibility Rule

Existing `evaluate_action(...)` may remain temporarily as a convenience shim, but it SHALL delegate to the new evaluator and SHALL NOT become the long-term authoritative API.

---

## 21. Minimum Test Matrix

### 21.1 Unit Tests

- allow low-risk, lawful, approved action
- block autonomous actuation without approval
- block missing jurisdiction basis
- escalate high-risk action
- require additional consent for scope expansion
- quarantine invalid artifact signature
- deny when evidence refs are missing for consequential actions
- expire stale approval artifact
- enforce reason-code stability

### 21.2 Integration Tests

- Core + Server artifact verification and deployment gate
- Core + Meta veto propagation preservation
- restore blocked under integrity failure
- merge blocked under unresolved policy conflict
- Safe Mode scoped to one node
- Safe Mode escalated fleet-wide only under contagious/systemic threat class

### 21.3 Adversarial Tests

- replayed approval artifact
- forged jurisdiction hint
- manipulated risk classification
- tampered policy bundle
- compromised node attempting federation vote
- emotional manipulation prompt requesting unsafe dependency escalation

### 21.4 Performance Tests

- critical deny path under 400μs target with hot cache
- interactive explanation path under 4ms
- quarantine decision under degraded network conditions
- audit emit path without blocking critical enforcement

---

## 22. Migration Plan

### Phase 1 — Formalize Current Gate
- preserve existing block conditions
- add canonical reason codes
- emit `PolicyResult`
- add audit record emission

### Phase 2 — Expand Enforcement
- integrate attestation, signature, and trust inputs
- add consent validation
- add Safe Mode and quarantine controllers
- add signed enforcement envelopes

### Phase 3 — Federation Binding
- integrate GAIA-Meta veto preservation
- propagate scoped protective states across nodes
- add distributed audit replay and review workflows

### Phase 4 — Advanced Protective Intelligence
- predictive threat analytics
- adaptive but bounded policy tuning
- richer human oversight and review tooling
- formal verification of hard constraints for critical action classes

---

## 23. Non-Negotiable Invariants

1. GUARDIAN may be reviewed, but not silently bypassed.
2. High-risk autonomous actuation requires human approval.
3. Missing jurisdiction basis blocks consequential action.
4. Safety and legality outrank convenience and throughput.
5. Quarantine preserves evidence.
6. Protective intervention must be scoped and reversible where possible.
7. All consequential decisions are auditable.
8. Policy enforcement semantics must be consistent across nodes.
9. No emotional or relational manipulation may be justified as safety.
10. Emergency override without post-incident review is invalid.

---

## 24. Acceptance Criteria

This spec is satisfied when:

- `GuardianEvaluator.evaluate(PolicyInput) -> PolicyResult` exists,
- reason codes are stable and covered by tests,
- audit records are emitted for consequential actions,
- Safe Mode and quarantine semantics are implemented,
- attestation / integrity signals influence enforcement,
- GAIA-Meta preserves GUARDIAN veto envelopes,
- autonomous high-risk action without approval is impossible through supported APIs,
- stale or forged approval artifacts are rejected,
- performance gates are met for critical enforcement paths.

---

## 25. Summary

GUARDIAN is the binding protective conscience of GAIA in operational form.

It exists to ensure that GAIA does not merely reason about safety and ethics, but **acts under them**, **halts under them**, **escalates under them**, and **proves that it did so**.

This specification therefore defines GUARDIAN as:

- the authorization gate,
- the protective enforcer,
- the legal and jurisdictional checker,
- the integrity and quarantine authority,
- the Safe Mode controller,
- and the auditable veto layer that preserves human dignity, lawful conduct, system integrity, and life-aligned operation across the entire GAIA architecture.
