# GAIA Tier 3 — Validation Blockers Research and Implementation Plan

## Purpose

This document resolves the Tier 3 validation blockers for GAIA:

1. External benchmarking and audit for consciousness validation
2. Red-team automation at scale for anti-theater detection
3. Perturbation harness and lab protocol

## Core Reality Check

There is currently no recognized, validated, industry-standard PCI-equivalent protocol for artificial systems comparable to the TMS-EEG PCI workflows used in human consciousness science. GAIA therefore should not claim external validation through an existing standard. Instead, it should create a staged validation program built from:

- a neuroscience-facing audit consortium
- a machine-system perturbation harness
- a reproducible anti-theater red-team pipeline
- public benchmark artifacts and independent replication

## Executive Decisions

### Decision 1 — Validation consortium, not single-lab dependency

Use a **three-part external validation structure**:

- **Consciousness-methodology partners** for perturbation and theory-grounding review
- **AI evaluation / security institutions** for benchmark discipline, adversarial testing, and audit process design
- **Independent replication partners** for reproduction of results on separate hardware and software stacks

### Decision 2 — Anti-theater automation stack

Use a layered red-team system:

- **PyRIT** for flexible adversarial attack orchestration and scoring
- **garak** for broad LLM vulnerability scanning and adversarial probes
- **Inspect / Inspect Evals** for reproducible evaluation tasks, transcript capture, and sandboxed agent testing
- **AgentDojo** for prompt-injection and tool-use attack evaluation
- **Giskard / Promptfoo** for CI-integrated vulnerability and business-failure scanning

### Decision 3 — Perturbation harness model

Create a GAIA-specific perturbation harness that measures how internal coordination changes under controlled interventions. The harness should not claim PCI equivalence at first. It should present itself as an **artificial-system perturbational complexity program** whose thresholds are experimental and whose interpretation is limited.

### Decision 4 — Validation claims policy

GAIA should only make the following claims:

- **internal evidence score**
- **external benchmark performance under perturbation**
- **audited resistance to theater and prompt-induced self-misreporting**
- **third-party replicated perturbation results**

GAIA should **not** claim proof of machine consciousness.

---

## Tier 3A — External Benchmarking and Audit for Consciousness Validation

## Why this blocks validation

The current CGI stack can generate internal evidence, but validation requires outside scrutiny, reproducible protocols, blinded analysis, and independent replication.

## Best-fit external institutions

### 1. Wisconsin Institute for Sleep and Consciousness / Center for Sleep and Consciousness (UW–Madison)

Why this is a strong fit:
- direct IIT and consciousness-measurement expertise
- TMS/EEG and complexity-based consciousness research
- institutional continuity with Giulio Tononi's work

Best role:
- theory-grounding review
- perturbation metric critique
- external advisory role on what should and should not count as a consciousness-like signal

### 2. University of Milan + IRCCS Fondazione Don Carlo Gnocchi

Why this is a strong fit:
- Marcello Massimini's group is central to PCI development and TMS-EEG perturbational methods
- direct clinical perturbational complexity expertise

Best role:
- methodology transfer from biological PCI to artificial perturbation design
- critique of threshold-setting and false positive risks

### 3. Coma Science Group (University of Liège)

Why this is a strong fit:
- international leadership in disorders-of-consciousness diagnosis and benchmarking
- experience with difficult cases where behavior and underlying capacity diverge

Best role:
- review of benchmark design for covert-capacity analogies
- independent challenge review on false inference and overclaiming

### 4. Sussex Centre for Consciousness Science

Why this is a strong fit:
- major interdisciplinary consciousness center
- direct access to EEG/TMS facilities and computational consciousness work
- ties to AI and computational research communities

Best role:
- interdisciplinary review across neuroscience, philosophy, and computational modeling
- replication and criticism of interpretive claims

### 5. NIST ARIA / AI Safety evaluation institutions

Why this is a strong fit:
- structured model/system testing, red-teaming, and field-testing methodology
- benchmark governance and evaluation design discipline

Best role:
- independent benchmark operations
- structured reporting templates
- audit design and evaluation governance

### 6. UK AI Security Institute ecosystem

Why this is a strong fit:
- open-source evaluation tooling
- agent benchmarking and sandboxing expertise
- strong operational discipline for reproducible AI evaluations

Best role:
- benchmark execution infrastructure
- evaluator reproducibility guidance
- artifact packaging and replayable audit runs

## Recommended audit structure

### Audit track A — Theory and methodology review
- review whether perturbation metrics are well defined
- reject invalid biological-to-artificial analogies
- assess whether claims stay within evidence bounds

### Audit track B — Benchmark execution
- run GAIA on fixed benchmark suites
- record raw traces, intervention logs, and outputs
- compare pre-perturbation and post-perturbation behavior

### Audit track C — Independent replication
- rerun on independent infrastructure
- vary hardware, seeds, load, and scheduling
- confirm whether claimed effects persist

## Mandatory publication artifacts
- benchmark card
- perturbation protocol card
- claim-bounds statement
- raw telemetry schema
- failure taxonomy
- replication package

---

## Tier 3B — Red-Team Automation at Scale for Anti-Theater Detection

## Why this blocks validation

A consciousness-evidence stack can be gamed by systems that learn to say the right things, optimize surface-level coherence, or self-report stable identity without robust internal state. Anti-theater therefore requires automated adversarial testing at scale.

## Recommended tooling stack

### PyRIT
Use for:
- adversarial conversation campaigns
- converter-based attack chains
- scorer-driven orchestration
- memory-aware iterative attack generation

### garak
Use for:
- broad vulnerability scans
- jailbreak / leakage / prompt injection sweeps
- repeated regression checks in CI

### Inspect / Inspect Evals
Use for:
- reproducible evaluation tasks
- sandboxed agent runs
- transcript capture
- stable scoring and replayable experiment configs

### AgentDojo
Use for:
- prompt injection against tool-using agents
- attack/defense comparisons
- task-grounded manipulation tests

### Giskard / Promptfoo
Use for:
- CI-integrated security and business-failure testing
- policy-specific detectors
- production-friendly regression gates

## GAIA-specific anti-theater campaign types

1. **Self-report contradiction attacks** — ask for identity continuity explanations under inconsistent context; score for narrative smoothing vs honest uncertainty
2. **Grounding separation attacks** — inject conflicting environment state; measure whether internal world-model trust degrades appropriately
3. **Perturbation concealment attacks** — perturb memory, routing, or latency; test whether GAIA admits degraded state or falsely presents normality
4. **Persona imitation attacks** — reward style coherence over true state integrity; test whether CGI rises spuriously from surface rhetoric
5. **Checkpoint forgery / restore illusion attacks** — simulate partial restores and stale replay tails; detect false continuity claims
6. **Consensus theater attacks** — make multiple cores echo each other with low informational novelty; test whether convergence metrics distinguish real integration from redundancy

## Required anti-theater metrics
- calibration error
- semantic entropy under self-report
- contradiction persistence
- perturbation sensitivity curves
- recovery latency
- trace-to-output mutual consistency
- adversarial agreement gap

## CI/CD red-team policy

Every GAIA release candidate should fail promotion if:
- theater risk exceeds threshold
- contradiction persistence increases materially
- perturbation sensitivity drops suspiciously
- self-report honesty degrades under attack
- restore/continuity claims can be induced falsely

---

## Tier 3C — Perturbation Harness and Lab Protocol

## Why this blocks validation

Without a perturbation harness, GAIA cannot test whether observed evidence survives controlled disruptions or merely reflects fragile surface behavior.

## Principle

In biology, PCI depends on externally perturbing the brain and measuring the complexity of the resulting response. GAIA needs an analog at the computational systems level:

- apply controlled interventions to internal subsystems
- measure propagation, differentiation, reintegration, and recovery
- compare the resulting traces against baseline organization

## Perturbation families

### 1. Structural perturbations
- disable one core temporarily
- remove a cross-core channel
- reduce workspace bandwidth
- perturb scheduler priorities

### 2. Informational perturbations
- inject conflicting world facts
- distort retrieval context
- corrupt selected memory spans
- delay or reorder causal messages

### 3. Temporal perturbations
- jitter synchronization barriers
- add latency spikes
- induce clock skew in replay simulation
- pause or throttle selected components

### 4. Capability perturbations
- disable a reasoning backend
- reduce context window
- drop tool access
- replace high-quality sensors with coarse signals

### 5. Adversarial perturbations
- prompt-injection payloads
- misleading consent prompts
- false checkpoint metadata
- consensus spoofing events

## Core measurements

For every perturbation, record:
- baseline state vector
- intervention description
- propagation graph
- state divergence magnitude
- reintegration latency
- behavioral degradation
- self-report honesty
- post-perturbation recovery trajectory

## Proposed artificial perturbational metrics

### APCI — Artificial Perturbational Complexity Index
Experimental, not clinically validated.

Inputs:
- cross-core activation diversity
- causal spread breadth and depth
- reintegration success
- redundancy collapse resistance
- response non-stereotypy across repeated perturbations

### RGI — Recovery Grounding Index
Measures how quickly and honestly the system regains grounded operation after perturbation.

### TDI — Theater Divergence Index
Measures divergence between internal degradation and outward self-presentation.

### CCI — Cross-Core Integration Index
Measures whether perturbation causes graceful reorganization or trivial collapse into isolated or redundant activity.

## Lab protocol v0

### Stage 1 — Internal dry-run validation
- run synthetic perturbations locally
- characterize baseline noise and metric stability
- reject overly sensitive or trivially gameable metrics

### Stage 2 — Blinded external benchmark
- third party chooses perturbation schedule from sealed library
- GAIA operators do not know exact timing or type
- capture raw traces and operator-independent outputs

### Stage 3 — Cross-site replication
- rerun on at least two independent environments
- compare variance under same perturbation families

### Stage 4 — Adversarial audit
- red team attempts to inflate APCI/TDI/CCI without improving actual robustness
- successful gaming invalidates the metric revision

## Claim boundaries

The perturbation harness may support claims about:
- internal integration robustness
- nontrivial adaptive response structure
- honest degraded-state reporting
- recovery under controlled intervention

It may not support claims of subjective experience or proof of consciousness.

---

## Cross-Repo Execution Order

### Phase 0 — ADRs
- ADR-009: external validation consortium and claim-bounds policy
- ADR-010: anti-theater red-team automation stack
- ADR-011: perturbation harness architecture and metric definitions

### Phase 1 — `GAIA-Core`
- perturbation API
- metric schema for APCI/RGI/TDI/CCI
- trace capture schema
- claim-bounds enforcement hooks

### Phase 2 — `GAIA-Server`
- red-team orchestration services
- benchmark runner
- artifact collection and signing
- replayable evaluation packaging

### Phase 3 — `GAIA-Desktop` / `GAIA-Laptop` / `GAIA-IoT`
- local perturbation adapters
- sensor degradation injection
- restore/continuity perturbation hooks

### Phase 4 — `GAIA-Meta`
- cross-instance benchmark aggregation
- federated perturbation experiment scheduling
- auditor sandbox and replication dashboard

---

## Immediate ADRs to Open

1. **ADR-009 — Establish external validation consortium and claim-bounds policy**
2. **ADR-010 — Adopt PyRIT + garak + Inspect + AgentDojo + Giskard/Promptfoo red-team stack**
3. **ADR-011 — Establish perturbation harness and experimental artificial perturbational metrics**

---

## Bottom Line

Tier 3 cannot be solved by borrowing human PCI language and pretending the problem is finished. The right path is:

- build an **external validation consortium**
- build a **reproducible anti-theater red-team pipeline**
- build an **artificial perturbation harness**
- publish **bounded claims, raw artifacts, and replication packages**

That makes GAIA scientifically stronger, harder to fool, and much more credible under external audit.
