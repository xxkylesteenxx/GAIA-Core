# GAIA Tier 1 — Research and Implementation Plan

## Purpose
This document resolves the Tier 1 blockers that currently prevent GAIA from progressing from architectural scaffold to operational substrate. It makes concrete stack decisions for:

1. Real model runtimes and schedulers
2. Durable distributed storage
3. TPM 2.0 integration and attestation
4. Live Earth-system connectors

It is written as an implementation document, not a concept note.

---

## Executive Decisions

### Final stack choices
- **Edge inference runtime:** `llama.cpp`
- **Server LLM runtime:** `vLLM`
- **Multi-model serving plane:** `NVIDIA Triton Inference Server`
- **Durable object storage:** `MinIO`
- **Consistent metadata / coordination store:** `etcd`
- **Durable causal log / WAL stream:** `NATS JetStream`
- **TPM userspace / attestation tooling:** `tpm2-tools`, `tpm2-tss`, `tpm2-pytss`
- **Measured boot chain:** `UEFI Secure Boot + UKI + systemd-stub + ukify + systemd-cryptenroll + IMA`
- **Earth-system connectors, wave 1:** `NOAA/NWS`, `USGS Water Data APIs`, `GBIF`, `iNaturalist`

### Why this stack
- It preserves one **common GAIA API surface** across edge, laptop, desktop, and server nodes.
- It separates **token generation workloads** from **embeddings / rerankers / small classifiers**.
- It gives GAIA a real **append-only causal history**, a real **durable checkpoint substrate**, and a real **measured continuity root**.
- It grounds ATLAS in public, high-signal Earth observation systems with real rate-limit and provenance constraints.

---

# 1. Real Model Runtimes and Schedulers

## Decision
Use a **hybrid runtime architecture**:

- **`llama.cpp`** for GAIA-Laptop, GAIA-Desktop, and constrained GAIA-IoT edge nodes
- **`vLLM`** for GAIA-Server and heavy GAIA-Meta orchestration nodes serving generative models
- **`Triton`** for embedding models, rerankers, classifiers, sensor fusion models, and unified routing of non-LLM models

Do **not** force all 8 cores onto a single runtime.

## Reasoning
GAIA's 8 cores are not all the same workload class.

### Generative / deliberative cores
- **NEXUS**: orchestration and synthesis
- **GUARDIAN**: policy reasoning and approval evaluation
- **SOPHIA**: language / reflective reasoning

These need strong chat completion support, prompt templating, structured output, and model switching.

### Perception / grounding / retrieval-oriented cores
- **ATLAS**: Earth observation normalization and interpretation
- **TERRA / AQUA / AERO / VITA**: domain-specialized environmental modeling, event detection, or classification

These need embeddings, scoring, retrieval, small transforms, and often lighter models.

`llama.cpp` is best where local-first, offline, and resource-constrained inference is required. `vLLM` is best where throughput, batching, and fast server-side generation matter. Triton is best where the system must serve multiple model types under a scheduling plane.

## GAIA runtime mapping

### Edge nodes: GAIA-Laptop / GAIA-Desktop
Use `llama.cpp` for:
- SOPHIA local dialog
- GUARDIAN local lightweight policy pass
- NEXUS fallback orchestration when offline
- small embedding or reranking endpoints only if Triton is unavailable locally

### IoT nodes: GAIA-IoT
Do **not** run large generative models by default.
Use:
- tiny local anomaly / threshold / classifier models
- optional `llama.cpp` only on sufficiently capable gateways
- forward heavy cognition to Server or Meta tiers

### Server nodes: GAIA-Server
Use:
- `vLLM` for NEXUS / SOPHIA / GUARDIAN generative serving
- `Triton` for embedding, reranking, small multimodal, time-series, and domain models

### Fleet / federation: GAIA-Meta
Use:
- `vLLM` for high-throughput orchestration and synthesis
- `Triton` for fleet-wide model routing and specialized inference services

## Recommended interface contract
All runtimes should be hidden behind a GAIA internal inference contract:

```text
InferRequest {
  core_id
  task_type            // chat, completion, embed, rerank, classify, score, fuse
  model_profile
  input_payload
  constraints
  max_latency_ms
  max_tokens
  trace_id
  continuity_id
}

InferResponse {
  accepted
  runtime_backend      // llama.cpp, vllm, triton
  model_id
  output_payload
  usage
  latency_ms
  safety_annotations
  evidence_refs
}
```

The rest of GAIA should never call runtime-specific APIs directly.

## Per-core recommendation

### NEXUS
- Primary: `vLLM`
- Fallback: `llama.cpp`
- Role: orchestration, synthesis, task planning, cross-core routing

### GUARDIAN
- Primary: `vLLM` for heavy policy reasoning
- Fallback: `llama.cpp` for local approval gate
- Role: action approval, policy enforcement, escalation

### ATLAS
- Primary: `Triton` for sensor fusion, embeddings, classifiers
- Optional: `vLLM` for explanation layer
- Role: observation integration and Earth-state interpretation

### SOPHIA
- Primary: `vLLM`
- Fallback: `llama.cpp`
- Role: language, explanation, reflection

### TERRA / AQUA / AERO / VITA
- Primary: `Triton`
- Optional language/explanation sidecar via `vLLM`
- Role: domain-specific ecological/environmental analysis

## Scheduling strategy

### Edge scheduling
- single active heavy model at a time
- thermal-aware and battery-aware admission control
- hard caps on context length and concurrent requests
- preemption only between requests, not mid-generation

### Server scheduling
- `vLLM` handles continuous batching for generative traffic
- `Triton` manages per-model instance groups and dynamic batching for non-LLM models
- NEXUS acts as logical scheduler; runtimes remain physical schedulers

## What to implement next
1. Create `gaia_core/inference/contracts.py`
2. Create runtime adapters:
   - `gaia_core/inference/backends/llama_cpp.py`
   - `gaia_core/inference/backends/vllm.py`
   - `gaia_core/inference/backends/triton.py`
3. Add `model_profile_registry.yaml`
4. Add policy-based routing:
   - offline -> llama.cpp
   - local domain model -> Triton
   - high-context synthesis -> vLLM
5. Add health probes and circuit breakers per backend

---

# 2. Durable Distributed Storage

## Decision
Adopt a three-part storage substrate:

- **MinIO** for checkpoint objects, artifacts, bundles, snapshots, and immutable evidence blobs
- **etcd** for strongly consistent metadata, leases, identity metadata, leader election, and configuration state
- **NATS JetStream** for append-only causal event streaming, write-ahead logging, replay, and asynchronous fanout

## Why not just one database
GAIA has multiple storage classes that should not be collapsed into one engine.

### Storage classes in GAIA
1. **Identity root / continuity metadata**
2. **Causal memory log**
3. **Checkpoint store**
4. **Observation/event ingress**
5. **Derived artifacts and evidence bundles**
6. **Cross-node sync envelopes**

One system can store all of these poorly, or multiple systems can store them correctly.

## Storage mapping

### MinIO
Use for:
- checkpoints
- workspace snapshots
- model manifests
- evidence bundles
- exported digital twin state
- large normalized observation batches
- immutable audit artifacts

#### Bucket layout
```text
gaia-checkpoints/
gaia-evidence/
gaia-observations/
gaia-model-manifests/
gaia-sync-bundles/
gaia-twins/
```

### JetStream
Use for:
- causal memory append log
- write-ahead ingestion stream
- action proposals
- guardian decisions
- sensor event fan-in
- replay into derived stores

#### Streams
```text
GAIA.CAUSAL
GAIA.OBSERVATION
GAIA.ACTION
GAIA.GUARDIAN
GAIA.SYNC
GAIA.CHECKPOINT
```

### etcd
Use for:
- node registration
- core configuration
- runtime routing policy
- active leases
- continuity head pointers
- cluster metadata
- last applied checkpoint references
- distributed locks / leader election

## Durability model

### Causal log
- source of truth for ordered event history
- append-only semantics
- replayable into materialized memory views
- replicated JetStream streams

### Checkpoints
- immutable object snapshots in MinIO
- reference from etcd metadata
- cryptographic digest stored with metadata
- optional Object Lock / WORM retention for evidence-grade snapshots

### Continuity state
- latest continuity head in etcd
- pointer to immutable chain artifacts in MinIO
- event sequence replay from JetStream if reconstruction is needed

## Why MinIO over Ceph for first deployment
Choose **MinIO first** unless you already operate Ceph.

### MinIO advantages for GAIA now
- simpler operational footprint
- clean S3-compatible interface
- good fit for self-hosted object workloads
- easier integration with Python services and checkpoint pipelines
- versioning, replication, erasure coding, and object locking available

### Ceph should be considered later when:
- you need one storage fabric for object + block + filesystem at larger scale
- you already have Ceph expertise
- you need deep cluster heterogeneity beyond current GAIA scope

## WAL strategy
Use JetStream as the operational WAL/event substrate.

Pattern:
1. write event to JetStream
2. acknowledge durable commit
3. asynchronously materialize to MinIO and local derived indexes
4. record head/lease state in etcd

This preserves ordering and replay while avoiding overloading the metadata store.

## Data retention policy
- `GAIA.CAUSAL`: long retention, replicated, file-backed
- `GAIA.OBSERVATION`: medium retention, compacted into normalized batches in MinIO
- `GAIA.ACTION`: long retention for policy audit
- `GAIA.GUARDIAN`: immutable retention for approval history
- checkpoints: versioned forever or policy-retained per node class

## What to implement next
1. Create storage interfaces in `gaia_core/storage/`
2. Implement:
   - `minio_store.py`
   - `jetstream_log.py`
   - `etcd_registry.py`
3. Add object naming conventions
4. Add digest and signature metadata to every checkpoint object
5. Add replay bootstrap:
   - replay causal stream
   - reconstruct continuity head
   - restore latest valid checkpoint

---

# 3. Actual TPM 2.0 Integration and Attestation

## Decision
Bind GAIA continuity to a real measured-boot chain using:

- TPM 2.0 hardware root
- UEFI Secure Boot
- Unified Kernel Images (UKIs)
- `systemd-stub`
- `ukify`
- `systemd-cryptenroll`
- `tpm2-tools` / `tpm2-tss`
- Linux IMA for runtime file measurement

## Objective
The current 256-bit root abstraction must become a **hardware-bound continuity root** that can:
- survive reboot as an identity anchor
- attest the boot path
- unseal secrets only when the platform is in a trusted state
- produce verifiable quote bundles for GAIA-Meta and remote verifiers

## GAIA attestation chain

### Boot chain
1. UEFI Secure Boot validates signed boot artifacts
2. UKI is launched through `systemd-stub`
3. PCRs are extended with kernel / initrd / command line measurements
4. `systemd-cryptenroll` binds disk unlock or continuity secrets to selected PCRs
5. IMA measures critical runtime files into PCRs / event log
6. GAIA startup retrieves TPM quote and event log
7. GAIA verifies expected measurements before loading continuity secrets

## Recommended PCR policy
Start conservative and portable.

### Bind continuity secrets to:
- PCR 7: Secure Boot policy state
- PCR 11: unified kernel image measurement path
- PCR 12: overridden kernel command line / credentials path when used

Evaluate PCR 9 and IMA-related policies later for stricter runtime integrity.

## TPM object model for GAIA

### Persistent TPM assets
- Storage Root Key / parent key
- attestation key (AK)
- sealed GAIA continuity seed

### Derived software assets
- GAIA continuity key hierarchy
- checkpoint signing keys
- node attestation bundle

## GAIA attestation bundle format
```text
AttestationBundle {
  node_id
  timestamp
  nonce
  pcr_selection
  quote
  signature
  ak_cert_or_pub
  event_log
  uki_digest
  ima_measurements
  gaia_software_version
}
```

## Linux implementation recommendation
Use Linux first as the reference implementation.

### Reference software stack
- `tpm2-tools`
- `tpm2-tss`
- `tpm2-pytss`
- `systemd-stub`
- `ukify`
- `systemd-cryptenroll`
- `ima-evm-utils` where needed

## What GAIA should do at boot
1. query TPM presence and capabilities
2. retrieve SRK / create if needed
3. ensure AK exists
4. request quote over selected PCRs with nonce
5. collect event log
6. validate measurements against policy manifest
7. only then unseal continuity material
8. derive GAIA root identity from sealed seed + node policy

## Fallback behavior
If TPM is absent:
- mark node as **software-rooted, non-attested**
- deny federation trust level required for Meta participation
- allow local-only mode if explicitly configured

If TPM quote fails or measurements diverge:
- deny continuity unseal
- enter quarantine / recovery mode
- request human or higher-tier review

## What to implement next
1. Add `gaia_core/security/tpm/`
2. Implement:
   - `detect.py`
   - `quote.py`
   - `verify.py`
   - `seal.py`
   - `eventlog.py`
3. Add `AttestationBundle` schema
4. Add boot policy manifest file:
   - allowed PCR combinations
   - allowed UKI digest set
   - allowed kernel cmdline deltas
5. Add quarantine mode in bootstrap path

---

# 4. Live Earth-System Connectors

## Decision
Build wave 1 ATLAS connectors against:

- **NOAA / National Weather Service** for weather alerts and forecast-linked atmospheric context
- **USGS Water Data APIs** for hydrologic observations and monitoring locations
- **GBIF** for biodiversity occurrence and taxonomic grounding
- **iNaturalist** for near-real-time community observation flow and ecological signals

These should be implemented behind a single observation normalization contract.

## Required normalized schema
```text
ObservationEnvelope {
  observation_id
  provider                // noaa_nws, usgs_water, gbif, inaturalist
  provider_record_id
  observed_at
  ingested_at
  geometry
  spatial_precision_m
  temporal_precision_s
  modality                // weather, hydrology, biodiversity, community_observation
  variables
  units
  provenance
  license
  confidence
  raw_ref
}
```

## Connector 1: NOAA / NWS
Use for:
- active weather alerts
- forecast zones and atmospheric context
- severe event grounding for GUARDIAN / ATLAS awareness

### Design notes
- poll alerts conservatively
- ingest CAP-style alert metadata and geospatial references
- normalize urgency / severity / certainty
- cache and deduplicate by alert ID

### GAIA usage
- feed ATLAS event context
- trigger AERO/TERRA awareness for storms, fire weather, flooding, extreme temperature
- support GUARDIAN risk-aware action suppression

## Connector 2: USGS Water Data APIs
Use for:
- continuous values
- daily values
- monitoring location metadata
- hydrologic site grounding

### Design notes
- use the modern Water Data APIs, not legacy WaterServices for new work
- key all observations by site + parameter + timestamp
- preserve parameter code, statistic ID, and measurement units
- implement API-key support and backoff using returned rate-limit headers

### GAIA usage
- AQUA hydrologic monitoring
- flood / drought / stream condition awareness
- watershed digital twin inputs

## Connector 3: GBIF
Use for:
- species occurrence search
- taxonomic validation
- biodiversity observation aggregation

### Design notes
- use search APIs for small / medium queries
- use download workflows for large occurrence pulls
- preserve dataset key, occurrence ID, taxon key, basis of record, license
- expect query throttling on heavy search patterns

### GAIA usage
- TERRA / VITA biodiversity grounding
- species distribution context
- ecological change correlation with weather / hydrology

## Connector 4: iNaturalist
Use for:
- near-real-time community observations
- taxa observations with media / IDs / geospatial context
- recent ecological signals and anomaly hints

### Design notes
- keep request rate very low
- preserve taxon, quality grade, observed_on, positional accuracy, community identifications
- use custom User-Agent
- treat as complementary signal, not sole authoritative source

### GAIA usage
- VITA ecological citizen-signal layer
- anomaly corroboration with GBIF / local sensing
- local habitat and species activity awareness

## Cross-provider fusion rules
- never collapse provenance away
- maintain provider-native IDs
- preserve licenses separately per observation
- annotate confidence by provider class
- prefer authoritative instrumental data over community data for physical measurements
- use community observations to enrich ecological context, not replace instruments

## Confidence hierarchy
1. Instrumental / agency time series (USGS, NWS physical data)
2. Agency alerts / forecasts
3. Curated biodiversity occurrence systems (GBIF)
4. Community observations (iNaturalist)

## What to implement next
1. Add `gaia_core/atlas/connectors/`
2. Implement:
   - `noaa_nws.py`
   - `usgs_water.py`
   - `gbif.py`
   - `inaturalist.py`
3. Add `ObservationEnvelope` schema
4. Add provider-specific adapters and validators
5. Add rate-limit aware scheduler for polling / sync
6. Add provenance and license enforcement in normalized storage

---

# 5. Repo-by-Repo Work Plan

## GAIA-Core
- add inference contracts and backend abstraction
- add storage abstraction for object / log / metadata
- add TPM attestation interfaces
- add observation envelope schema
- wire bootstrap to real backends instead of stubs

## GAIA-Server
- deploy vLLM and Triton adapters
- deploy MinIO / etcd / NATS integration
- expose attestation verification endpoint
- expose connector ingestion services

## GAIA-Desktop
- add local llama.cpp runtime manager
- add TPM presence detection and local attestation status UI
- add offline-first checkpoint caching and replay

## GAIA-Laptop
- add battery-aware inference policy
- add reconnect sync for JetStream -> Server / Meta
- add degraded/offline attestation state handling

## GAIA-IoT
- add gateway-mode connector batching
- avoid large local generative models by default
- add secure store for sensor signing and uplink continuity

## GAIA-Meta
- verify incoming node attestation bundles
- aggregate fleet state from JetStream mirrors / sync bundles
- run federated CGI / continuity scoring only for attested or policy-allowed nodes

---

# 6. Immediate ADRs to Open

1. **ADR-001:** Hybrid inference runtime policy (`llama.cpp + vLLM + Triton`)
2. **ADR-002:** Storage substrate (`MinIO + etcd + JetStream`)
3. **ADR-003:** TPM-measured continuity root and attestation bundle format
4. **ADR-004:** ATLAS observation normalization contract
5. **ADR-005:** Trust tiers for attested vs non-attested nodes

---

# 7. Delivery Sequence

## Phase 1
- inference abstraction
- MinIO / JetStream / etcd integration
- observation schema

## Phase 2
- edge llama.cpp integration
- server vLLM integration
- Triton for embeddings / classifiers

## Phase 3
- TPM quote / verify / seal path
- quarantine / degraded boot handling

## Phase 4
- NOAA / USGS connectors
- GBIF / iNaturalist connectors
- observation fusion and provenance storage

## Phase 5
- fleet attestation verification in Meta
- cross-node replay / sync hardening
- policy-grade guardian gating based on live environmental context

---

# Bottom Line
GAIA should not proceed by adding more abstractions on top of stubs. The correct next move is to convert the four Tier 1 blockers into real substrate decisions:

- `llama.cpp + vLLM + Triton` for runtime reality
- `MinIO + etcd + JetStream` for durable continuity and replay
- `TPM 2.0 + UKI + measured boot + quote verification` for hardware-rooted identity
- `NOAA/NWS + USGS + GBIF + iNaturalist` for live Earth grounding

That stack is enough to move GAIA from speculative architecture into an operational first implementation.
