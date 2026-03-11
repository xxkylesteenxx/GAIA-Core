# GAIA Environmental Data Quality Specification v1.0

**Status:** Repo-ready architecture specification  
**Recommended path:** `GAIA-Core/data-quality/environmental/docs/GAIA_Environmental_Data_Quality_Spec_v1.0.md`  
**Scope:** sensor fusion, adversarial robustness, freshness/latency classification, RT/NRT management  
**Primary objective:** Prevent GAIA's environmental consciousness from reasoning over stale, poisoned, or incoherent inputs.

---

## 1. Executive Position

GAIA's environmental intelligence is only as good as its ingest discipline.

The correct design is:

1. **typed source classes**
2. **explicit latency classes**
3. **fusion with uncertainty**
4. **continuous anomaly and adversarial screening**
5. **policy-aware downgrade paths when quality falls**

---

## 2. Research-grounded conclusions

### 2.1 Heterogeneous sensor systems need a common interface
OGC SensorThings provides a unified, geospatially aware way to manage and retrieve observations and metadata from heterogeneous IoT sensor systems. GAIA should use SensorThings-compatible adapters wherever feasible.

### 2.2 Latency classes should follow Earth observation reality, not fantasy
NASA's Earthdata guidance is useful and concrete:
- **real-time:** under 1 hour
- **near real-time (NRT):** 1-3 hours
- **low latency:** 3-24 hours
- **expedited:** 1-4 days
- **standard routine processing:** typically 8-40 hours, sometimes much longer

### 2.3 NRT data is operationally valuable but not always science-grade
GAIA must track both **latency** and **quality tier** independently.

### 2.4 Fusion improves anomaly detection, but only with uncertainty-aware design
Mismatched spatial and temporal resolution, uncertainty, and heterogeneous sensor quality are first-order design problems.

---

## 3. Source taxonomy

```text
S1  regulatory-grade in situ sensors
S2  calibrated field stations
S3  low-cost distributed IoT sensors
S4  satellite / remote sensing products
S5  human / citizen reports
S6  derived model products
```

**Quality defaults:**
- S1/S2: high trust, still verify freshness and drift
- S3: medium trust, strong calibration and neighborhood checks
- S4: high coverage, latency and processing-level aware
- S5: low trust unless corroborated
- S6: never treat as raw truth; keep provenance to parents

---

## 4. Latency classification

```text
URT  ultra-real-time      <5 min
RT   real-time            <1 h
NRT  near-real-time       1-3 h
LL   low-latency          3-24 h
EXP  expedited            1-4 d
STD  standard-science     quality-prioritized reference
```

Every observation record must store: acquisition time, ingest time, publish time, latency class, quality class, processing level.

---

## 5. Data quality gates

**Required dimensions:** completeness, timeliness/freshness, spatial consistency, temporal consistency, calibration status, provenance completeness, uncertainty estimate, adversarial suspicion score.

**Gate outcomes:** `PASS` / `WARN` / `DEGRADE` / `FAIL` / `QUARANTINE`

---

## 6. Sensor fusion architecture

```text
Layer 1  intra-sensor cleaning
Layer 2  neighborhood consistency
Layer 3  multi-modal spatial-temporal fusion
Layer 4  model-assisted gap filling
Layer 5  domain-core interpretation
```

**Fusion rules:**
- never fuse away disagreement; preserve residuals
- retain source-level uncertainty
- keep original observations immutable
- store fusion lineage
- allow fallback to lower-resolution but higher-confidence sources

---

## 7. Adversarial and fault robustness

**Threat classes:** spoofed sensor readings, replayed packets, coordinated low-amplitude drift attacks, GPS/time manipulation, compromised citizen reports, model-derived contamination.

**Response:** isolate suspect stream, downgrade source weight, request corroboration, retain in forensic store, prevent actuation decisions from using quarantined data.

---

## 8. Freshness debt

```text
freshness_debt = required_freshness - actual_freshness
```

When freshness debt rises, NEXUS should: prioritize re-ingest, demote stale analytics, switch user-facing explanations to uncertainty-forward mode, block actuation if corroboration falls below threshold.

---

## 9. Bottom line

GAIA should implement **latency-aware, uncertainty-aware, adversarial-aware environmental ingest**. Use SensorThings-style standardization, classify data by real operational latency classes, fuse with preserved uncertainty, and quarantine suspect streams aggressively.
