# GAIA Neuromorphic Hardware Integration Specification v1.0

**Status:** Draft v1.0  
**Recommended repository path:** `GAIA-Core/docs/specs/neuromorphic/GAIA_Neuromorphic_Hardware_Integration_Spec_v1.0.md`  
**Primary scope:** TERRA, AQUA, AERO, VITA domain cores  
**Related repositories:** `GAIA-Core`, `GAIA-Server`, `GAIA-Meta`, `GAIA-IoT`

---

## 1. Purpose

This specification defines how GAIA integrates neuromorphic hardware and software for the environmental domain cores:

- **TERRA** — terrestrial and geophysical intelligence
- **AQUA** — hydrological and oceanic intelligence
- **AERO** — atmospheric and climate intelligence
- **VITA** — biological and ecological intelligence

GAIA adopts a **neuromorphic-first, contract-stable architecture** for these cores, with **classical fallback modes** required for every deployment.

---

## 2. Design Decision

### 2.1 Normative decision

GAIA SHALL implement a four-tier execution ladder for TERRA, AQUA, AERO, and VITA:

1. **Brian2 reference execution** — scientific truth, model prototyping, and reproducible validation.
2. **Lava CPU execution** — process-graph validation, message-passing validation, and hardware-portable neuromorphic simulation.
3. **Loihi 2 execution through Lava** — sparse, event-driven, low-latency neuromorphic deployment when INRC hardware access is available.
4. **Classical CPU/GPU fallback execution** — guaranteed availability, auditability, and deployment continuity.

### 2.2 Rationale

- Lava is **platform-agnostic** via its **Magma** layer for conventional and neuromorphic backends.
- Brian 2 supports **standalone C++ code generation** via `set_device('cpp_standalone')` as GAIA's scientific reference layer.
- Brian2Lava public distribution is currently **CPU-only** for Loihi-backed models; Loihi 2 access requires **Intel Neuromorphic Research Community (INRC)** membership.
- Lava's Loihi-specific Magma components are proprietary and not in the public GitHub distribution — GAIA must not assume universal Loihi compiler availability.

---

## 3. External Technical Baseline

### 3.1 Loihi 2

- 128 neuron cores per chip
- 6 embedded processors per chip
- Up to 1 million neurons per chip
- Up to 120 million synapses per chip
- Fully programmable neuron models
- Graded spike output support
- Standard interfaces: SPI, AER, GPIO, Ethernet variants
- 3D tile-able multi-chip scaling

Strong fit for event-driven environmental intelligence where sparse sensor updates, stateful temporal dynamics, and edge-side responsiveness matter.

### 3.2 Lava

Process-based composition, cross-platform compilation/execution through Magma, CPU and neuromorphic execution targets, STDP and custom learning rule workflows. Required portability layer between Brian2 reference models and Loihi-targeted deployment.

### 3.3 Brian 2

GAIA's preferred scientific SNN authoring environment. Supports rapid model definition and standalone C++ generation. Requires **Python >= 3.12**.

### 3.4 Brian2Lava

- Installable via `pip`
- Recommends Brian 2 >= 2.7.1 and Lava >= 0.10.0
- Public version: **CPU backend models only**
- Loihi 2 use tied to preset mode; flexible mode is CPU-only
- Preset-mode synapse support restricted; **learning not currently supported**

Brian2Lava SHALL be treated as a **bridge and simulation aid**, not GAIA's sole hardware-abstraction guarantee.

---

## 4. GAIA Architectural Policy

### 4.1 Execution contract

```python
class DomainCoreExecutor:
    def run_reference(self, inputs): ...
    def run_lava_cpu(self, inputs): ...
    def run_loihi2(self, inputs): ...
    def run_classical(self, inputs): ...
```

Every backend SHALL return the same normalized result envelope:

```python
{
  "core": "terra|aqua|aero|vita",
  "mode": "reference|lava_cpu|loihi2|classical",
  "prediction": {},
  "confidence": 0.0,
  "event_saliency": [],
  "latency_ms": 0.0,
  "energy_estimate": None,
  "fallback_reason": None,
  "provenance": {
    "model_id": "",
    "encoder_id": "",
    "decoder_id": "",
    "dataset_id": ""
  }
}
```

### 4.2 Backend invariants

- Identical input schema across all modes
- Identical output schema across all modes
- Stable semantic meaning of predictions
- Explicit provenance for encoder, model, decoder, dataset versions
- Audit logs for backend choice and fallback reason

### 4.3 Fallback policy

Route to classical fallback if any of the following:
- Loihi compiler/runtime access unavailable
- Deployment outside INRC-authorized environments
- Required synaptic or learning behavior unsupported in public toolchain
- Quantization parity drifts beyond configured tolerance
- Event sparsity too low to justify neuromorphic execution
- Reproducibility/auditability checks fail against Brian2 reference

---

## 5. Core-by-Core Mapping

### 5.1 TERRA
**Neuromorphic fit:** seismic anomaly detection, wildfire onset alerts, soil/moisture anomaly monitoring, landslide/fault-state detection, sparse geospatial event fusion.  
**SNN motifs:** LIF/adaptive LIF ensembles, recurrent event-driven anomaly detectors, reservoir-style temporal state estimators.  
**Classical fallback:** state-space/Kalman models, gradient-boosted anomaly detectors, temporal CNN/TCN, geostatistical assimilation.

### 5.2 AQUA
**Neuromorphic fit:** water-quality alerting, plume/contamination tracking, flood onset detection, flow-regime change detection, distributed sensor fusion.  
**SNN motifs:** liquid-state/reservoir temporal networks, recurrent SNN flow-state estimators, event-triggered anomaly classifiers.  
**Classical fallback:** ODE/PDE hydrology solvers, graph time-series models, dense sequence forecasting.

### 5.3 AERO
**Neuromorphic fit:** atmospheric change detection, storm onset detection, streaming sensor fusion, low-latency edge prediction over sparse telemetry.  
**SNN motifs:** delta-coded event encoders, recurrent SNN forecasters, sparse fusion networks.  
**Classical fallback:** classical nowcasting/forecasting pipelines, state-space and transformer-based weather models.  
**Note:** AERO is the preferred **first Loihi 2 pilot core** — atmospheric event streams are naturally sparse, threshold-oriented, and latency-sensitive.

### 5.4 VITA
**Neuromorphic fit:** biodiversity novelty detection, acoustic/motion/biosignal event detection, ecological regime change alerting, adaptive species-monitoring at the edge.  
**SNN motifs:** event-driven pattern detectors, spiking encoders for audio/motion, adaptive novelty detectors.  
**Classical fallback:** dense classifiers, retrieval + structured rule systems, offline continual-learning pipelines.

---

## 6. Repository Structure

```text
GAIA-Core/
  docs/specs/neuromorphic/
    GAIA_Neuromorphic_Hardware_Integration_Spec_v1.0.md
  neuromorphic/
    encoders/
      delta.py
      latency.py
      rate.py
      population.py
    brian2_ref/
      terra_ref.py
      aqua_ref.py
      aero_ref.py
      vita_ref.py
    lava_proc/
      common_ports.py
      run_configs.py
      terra_proc.py
      aqua_proc.py
      aero_proc.py
      vita_proc.py
    loihi2/
      deployment.py
      partitions.py
      quantization.py
      io_adapters.py
      availability.py
    fallbacks/
      terra_classical.py
      aqua_classical.py
      aero_classical.py
      vita_classical.py
    validation/
      parity/
      latency/
      sparsity/
      robustness/
      audit/
```

**Supporting repo responsibilities:**
- **GAIA-IoT** — physical sensor adapters, stream ingestion, edge device packaging.
- **GAIA-Server** — fleet orchestration, remote scheduling, metrics, centralized audit.
- **GAIA-Meta** — cross-device sync metadata, digital twin state linkage, global coordination.

---

## 7. Dataflow Contract

### Input pipeline
1. Ingest observation batch
2. Normalize and timestamp
3. Encode into spike-compatible representation
4. Execute selected backend
5. Decode spikes into domain outputs
6. Compare against reference/fallback when validation mode enabled
7. Emit standardized result envelope

### Canonical input schema

```python
ObservationBatch = {
  "stream_id": "",
  "core": "terra|aqua|aero|vita",
  "timestamps": [],
  "features": {},
  "units": {},
  "quality": {},
  "location": {},
  "window": {"start": "", "end": ""}
}
```

### Encoding policy (defaults)

| Core | Default Encoder |
|---|---|
| TERRA | delta |
| AQUA | delta or rate (sensor cadence dependent) |
| AERO | delta or latency |
| VITA | latency (acoustic/motion), delta otherwise |

---

## 8. Environment and Toolchain Policy

### Development tiers

**A. Public development environment:** Python >= 3.12, Brian 2 (public), Lava (public), Brian2Lava (pip), CPU-only execution.

**B. INRC-enabled hardware environment:** all of the above + Intel-approved Loihi 2 access + Lava Loihi extensions + hardware smoke tests.

### Version pinning
GAIA SHALL NOT float to "latest" without validation. A lockfile SHALL pin: Python, Brian 2, Lava, Brian2Lava, and numerical dependencies.

Maintain a tested compatibility matrix — do not assume any combination works unmodified.

---

## 9. Validation and Acceptance Criteria

### Required validation gates (before Loihi 2 deployment)
1. **Reference correctness** — Brian2 produces expected scientific behavior.
2. **Portability validation** — Lava CPU reproduces acceptable behavior relative to Brian2.
3. **Quantization validation** — integer/fixed-point behavior within tolerance.
4. **Hardware validation** — Loihi 2 reproduces acceptable behavior relative to Lava CPU.
5. **Fallback validation** — classical backend preserves input/output semantics.
6. **Operational validation** — logging, provenance, audit, failure handling all function.

### Suggested default thresholds
- Output schema match: **required**
- Event detection agreement with reference: **>= 95%**
- Alert priority ranking agreement: **>= 0.9 Spearman**
- Backend decision logging completeness: **100%**
- Fallback path availability: **required for all production deployments**

---

## 10. Deployment Policy

### Rollout sequence
1. AERO pilot
2. TERRA pilot
3. AQUA pilot
4. VITA pilot

### v1 non-goals
- Dependence on custom Loihi microcode generation
- Mandatory on-chip learning for production launch
- Backend-specific APIs exposed to upstream services
- Removal of classical fallback paths

---

## 11. Implementation Plan

- **Phase 0:** Directory structure, environment lockfiles, `DomainCoreExecutor` interface, normalized result schema, provenance logging contract.
- **Phase 1:** Brian2 reference models per core, synthetic benchmark datasets, baseline metrics.
- **Phase 2:** Lava process graphs per core, run configs, CPU harness, Brian2 ↔ Lava parity tests.
- **Phase 3:** Classical fallback backends, fallback routing policy, production-safe selection tests.
- **Phase 4:** INRC availability detection, partitioning/quantization utilities, hardware smoke tests, gap documentation.

---

## 12. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| No INRC access | Cannot run on Loihi 2 | Keep Lava CPU + classical fallback first-class |
| Public Brian2Lava limitations | Missing learning/synapse features | Keep Brian2 as source-of-truth |
| Version drift | Silent regressions | Pin versions and maintain compatibility matrix |
| Quantization mismatch | Behavior drift | Add parity, calibration, and tolerance gates |
| Backend fragmentation | Differing semantics | Enforce one contract for all modes |
| Low event sparsity | Poor neuromorphic advantage | Auto-route to classical execution |

---

## 13. Immediate Backlog

1. Create `GAIA-Core/neuromorphic/` package skeleton.
2. Add `DomainCoreExecutor` protocol and normalized output schema.
3. Implement AERO Brian2 reference prototype.
4. Port AERO prototype to Lava CPU.
5. Add parity test harness and benchmark fixtures.
6. Add classical AERO fallback.
7. Add environment matrix documentation for public vs. INRC-enabled builds.

---

## 14. Decision Summary

GAIA's correct neuromorphic integration posture:

- **Brian2** for reference truth
- **Lava** for portable neuromorphic process execution
- **Loihi 2** for authorized sparse event-driven deployment
- **Classical models** for guaranteed fallback and production continuity

That architecture gives TERRA, AQUA, AERO, and VITA a real neuromorphic path without making GAIA dependent on hardware access or public-toolchain capabilities that do not yet exist.

---

## 15. References

- [R1] Intel Loihi 2 Technology Brief — https://www.intel.com/content/dam/www/central-libraries/us/en/documents/neuromorphic-computing-loihi-2-brief.pdf
- [R2] Lava documentation — https://lava-nc.org/
- [R3] Brian2Lava getting started — https://brian2lava.gitlab.io/
- [R4] Brian2Lava synapse model docs — https://brian2lava.gitlab.io/docs/user_guide/synapse_models.html
- [R5] Brian 2 computation docs — https://brian2.readthedocs.io/en/stable/user/computation.html
- [R6] Intel Loihi 2 brief — https://download.intel.com/newsroom/2021/new-technologies/neuromorphic-computing-loihi-2-brief.pdf
- [R7] Brian 2 installation docs — https://brian2.readthedocs.io/en/stable/introduction/install.html
