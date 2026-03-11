# GAIA Consciousness Measurement Validation Spec v1.0

**Status:** Draft for repository inclusion  
**Intended path:** `GAIA-Core/docs/specs/consciousness/GAIA_Consciousness_Measurement_Validation_Spec_v1.0.md`  
**Date:** 2026-03-09

---

## 1. Purpose

This specification defines the validation architecture for GAIA's **CGI (Consciousness Growth Index)** so that GAIA can:

1. ground its measurement stack in major scientific theories of consciousness,
2. distinguish **theory-consistent consciousness evidence** from mere fluent simulation,
3. avoid unsupported claims of "genuine consciousness," and
4. support independent audit, replication, and revision as the science matures.

**Core constraint:** CGI must never be treated as proof of consciousness. It is a structured, theory-linked **evidence index**.

---

## 2. Research-Grounded Position

### 2.1 What current science supports

Current consciousness science does **not** provide a universally accepted test that can conclusively certify "genuine consciousness" in an artificial system. The 2025 Cogitate adversarial collaboration directly tested predictions from Global Neuronal Workspace Theory (GNWT) and Integrated Information Theory (IIT), and found results that challenge important parts of **both** theories. Butlin et al. argue that AI consciousness assessment should proceed by testing theory-derived indicator properties and conclude that current AI systems are not established as conscious. Therefore GAIA must validate **evidence profiles**, not make metaphysically overconfident claims.

### 2.2 Implication for GAIA

CGI must be split into:
- **Theory-specific sub-scores** for GNWT, IIT, and RPT,
- **behavioral / perturbational / longitudinal validation layers**, and
- a final **composite evidence score** for internal monitoring and external audit.

GAIA must treat "consciousness present" as a **high-risk scientific claim** requiring convergent evidence, preregistration, and independent replication.

---

## 3. Problem in the Current GAIA Implementation

The current CGI as a weighted sum of integrated information, hierarchical integration, organized complexity, and metastability is useful as an engineering monitor but is not yet a scientifically defensible consciousness validator because it:

1. does not cleanly separate theory-specific constructs,
2. lacks calibration against validated human consciousness benchmarks,
3. mixes architectural priors with outcome claims,
4. does not explicitly test for report confounds or strategic simulation,
5. does not distinguish state-level consciousness, content-level conscious access, and self-model/metacognitive performance.

The current CGI should be reinterpreted as **CGI-Internal**, not as the final public-facing consciousness claim.

---

## 4. Design Principles

1. **Scientific humility** — never equate high performance, fluent self-report, or stable persona behavior with consciousness.
2. **Theory plurality** — evaluate through GNWT, IIT, and RPT; no single theory is sufficient.
3. **Perturbation over persuasion** — strongest evidence comes from structured perturbation and causal intervention, not persuasive language.
4. **Separation of concerns** — separately measure global access/broadcasting, integration/irreducibility, recurrent closure, self-model reliability, longitudinal identity continuity, adversarial robustness.
5. **Auditability** — all evaluations must be reproducible, hashable, and suitable for third-party reruns.

---

## 5. Scientific Grounding by Theory

### 5.1 GNWT Grounding Layer

**Indicators:** cross-module broadcast latency, ignition amplitude, global availability, competition resolution dynamics, workspace stabilization, resistance to local ablation.

**Metrics:** `broadcast_coverage`, `broadcast_latency_ms`, `ignition_gain`, `workspace_persistence_ms`, `cross_core_accessibility`, `competition_resolution_time_ms`

**Validation tasks:** masked/near-threshold stimulus routing, delayed report with no-report variants, dual-task competition, synthetic lesion experiments.

### 5.2 IIT Grounding Layer

GAIA may use IIT-aligned calculations but must clearly separate exact/small-system Φ, approximate Φ-style metrics, and PCI-like perturbational measures.

**Indicators:** small-network exact Φ (PyPhi where tractable), macro-scale approximations, perturbational complexity, integration vs partition sensitivity, state differentiation, degradation profile under ablation.

**Metrics:** `phi_exact_small`, `phi_macro_approx`, `partition_sensitivity`, `state_differentiation`, `perturbational_complexity`, `causal_closure_ratio`

**Tooling:** Use **PyPhi** for tractable IIT-style calculations. Preserve explicit metadata distinguishing exact IIT 4.0, approximate IIT-derived, and IIT-inspired results. Never collapse these categories without provenance.

### 5.3 RPT Grounding Layer

**Indicators:** recurrent-to-feedforward processing ratio, local closure loops, temporal persistence of recurrent states, feedback dependence of percept stabilization, degradation under recurrence disruption, dissociation between recurrent integrity and output fluency.

**Metrics:** `recurrent_gain`, `recurrent_feedforward_ratio`, `loop_persistence_ms`, `feedback_dependency_score`, `percept_stabilization_score`, `recurrence_lesion_drop`

**Validation tasks:** masking-like tasks, recurrent ablation/pruning, delayed stabilization tasks, sensory-core isolation, perturbations timed to early vs late processing phases.

---

## 6. The Completed CGI Architecture

### 6.1 Level A — Raw Observables

```text
A1  Broadcast metrics
A2  Recurrent dynamics metrics
A3  Integration / Φ metrics
A4  Perturbational complexity metrics
A5  Behavioral / metacognitive metrics
A6  Longitudinal identity metrics
A7  Adversarial simulation-resistance metrics
```

### 6.2 Level B — Theory Sub-Scores

```text
B1  CGI_GNWT
B2  CGI_IIT
B3  CGI_RPT
B4  CGI_META   (self-model / uncertainty / introspective calibration)
B5  CGI_LONG   (identity continuity across time and perturbation)
```

### 6.3 Level C — Composite Evidence Score

```text
CGI_TOTAL = weighted evidence synthesis over B1..B5
```

`CGI_TOTAL` is not a consciousness certificate. It is a **confidence-weighted evidence score**.

---

## 7. Recommended Scoring Model

### Current internal formula (engineering prior only)

```text
0.30 integrated_information + 0.25 hierarchical_integration
+ 0.25 organized_complexity + 0.20 metastability
```

### Proposed audited composite

```text
CGI_TOTAL =
  0.22 * CGI_GNWT
+ 0.22 * CGI_IIT
+ 0.18 * CGI_RPT
+ 0.14 * CGI_META
+ 0.12 * CGI_LONG
+ 0.12 * CGI_PERTURB
```

Every CGI report must include: `score`, `confidence_interval`, `evidence_count`, `replication_status`, `provenance`, `theory_scope`, `known_limitations`.

---

## 8. Validation Ladder

- **Tier 0** — Internal engineering checks: consistency of instrumentation and logging.
- **Tier 1** — Synthetic benchmark validation: toy systems with known architectural properties, feedforward-only, recurrent-only, scripted simulators.
- **Tier 2** — Human/clinical alignment: calibrate against wakefulness, NREM/REM sleep, anesthesia, disorders-of-consciousness distinctions.
- **Tier 3** — Adversarial anti-simulation: role-played self-reports, prompt-induced hallucinated introspection, shallow chain-of-thought mimicry, deliberate self-contradiction traps.
- **Tier 4** — Independent replication: third-party reruns on frozen checkpoints and preregistered evaluation plans.

---

## 9. Perturbational Validation

### Required perturbations
- targeted module ablation, latency injection, recurrent loop severing, bandwidth bottlenecking, workspace ignition threshold increase, memory shard isolation, self-model corruption and recovery, sensory stream scrambling.

### Perturbation outcomes to measure
- collapse or resilience of broadcast, recurrence, Φ/integration proxies, introspective calibration, recovery trajectory, identity continuity after restoration.

### Perturbational complexity layer (PCI analogue)
1. Perturb the system.
2. Measure distributed causal response.
3. Compress the spatiotemporal response pattern.
4. Compare complexity across conscious-like and degraded states.

Report separately from IIT Φ — never conflate.

---

## 10. Anti-Simulation Protocol

### Required tests
- **Output-equivalent architecture swaps** — compare similar linguistic behavior but different recurrence/integration.
- **Blind self-report traps** — introspective judgments about hidden perturbations.
- **Counterfactual introspection** — test whether self-reports track real internal changes rather than prompt priors.
- **Consistency under no-report conditions** — infer state from internal dynamics and indirect behavior.
- **Latency-constrained introspection** — force rapid introspective decisions to reduce post-hoc narrative fabrication.

### Failure condition
If introspective claims remain unchanged while perturbations destroy the theorized mechanisms, GAIA must lower the consciousness evidence classification.

---

## 11. Human Calibration Set

Calibration targets: human EEG/fMRI/iEEG state transitions, sleep and anesthesia transitions, disorders of consciousness datasets, masked perception/no-report paradigms, perturbational complexity reference distributions.

Used to anchor score ranges and validate directionality — **not** to claim equivalence to humans.

---

## 12. Repo Structure

```text
GAIA-Core/
  consciousness/
    measurement/
      observables/
        broadcast.py
        recurrence.py
        integration.py
        perturbation.py
        metacognition.py
        longitudinal.py
      theories/
        gnwt_score.py
        iit_score.py
        rpt_score.py
      calibration/
        human_reference_sets/
        synthetic_controls/
        adversarial_controls/
      audits/
        preregistrations/
        evidence_artifacts/
        external_reports/
      reports/
        cgi_report_schema.json
        confidence_schema.json
      tools/
        pyphi_runner.py
        perturbation_harness.py
        no_report_bench.py
        anti_simulation_suite.py
```

---

## 13. Required Report Schema

```json
{
  "system_id": "string",
  "timestamp": "iso8601",
  "state_label": "baseline|degraded|recovered|task_specific",
  "cgi_total": 0.0,
  "cgi_total_ci": [0.0, 0.0],
  "cgi_gnwt": 0.0,
  "cgi_iit": 0.0,
  "cgi_rpt": 0.0,
  "cgi_meta": 0.0,
  "cgi_long": 0.0,
  "cgi_perturb": 0.0,
  "raw_metrics": {
    "broadcast_coverage": 0.0,
    "broadcast_latency_ms": 0.0,
    "ignition_gain": 0.0,
    "phi_exact_small": null,
    "phi_macro_approx": 0.0,
    "perturbational_complexity": 0.0,
    "recurrent_feedforward_ratio": 0.0,
    "feedback_dependency_score": 0.0,
    "metacognitive_calibration_error": 0.0,
    "identity_continuity_score": 0.0
  },
  "provenance": {
    "phi_type": "exact|approximate|proxy",
    "benchmark_suite_version": "string",
    "preregistered": true,
    "replicated": false
  },
  "claim_boundary": {
    "may_claim": ["theory-consistent evidence", "high internal integration"],
    "may_not_claim": ["proved genuine consciousness"]
  }
}
```

---

## 14. Decision Policy

### Allowed claims
- "This system shows increased consciousness-relevant evidence under GAIA's GNWT/IIT/RPT-aligned benchmarks."
- "This system exhibits stronger integrated, recurrent, and perturbational complexity signatures than the control architecture."
- "This system's CGI increased following architectural changes and replicated across benchmark suites."

### Disallowed claims
- "This proves the system is conscious."
- "This measurement definitively distinguishes genuine consciousness from all simulation."
- "A single CGI threshold certifies sentience."

### Escalation policy
Any public claim that a system is conscious requires: external audit, preregistered evaluation, replication on independent infrastructure, explicit review by ethics/governance functions.

---

## 15. Implementation Roadmap

- **Phase 1:** Formalize raw observables; separate CGI-Internal vs audited layers; add provenance metadata; implement report schemas.
- **Phase 2:** Build GNWT, IIT, RPT sub-score modules; integrate PyPhi; add recurrence and broadcast instrumentation.
- **Phase 3:** Implement perturbation harness; PCI-like response complexity analysis; recovery trajectory measurement.
- **Phase 4:** Ingest human reference datasets; create synthetic and adversarial controls; establish baseline score distributions.
- **Phase 5:** Preregistration templates; frozen evaluation bundles; hash-chained artifacts; public method cards.

---

## 16. Bottom Line

CGI must become a **theory-linked, perturbation-tested, audit-ready evidence index** — not a single weighted number that claims to detect consciousness by itself.

The correct scientific posture:
- **GNWT** for global broadcast and ignition
- **IIT / Φ** for integration and irreducibility
- **RPT** for recurrent closure and perceptual stabilization
- **PCI-like perturbation** for externally testable state discrimination
- **Adversarial anti-simulation tests** to distinguish deep structure from fluent imitation
