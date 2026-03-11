# ADR-001: Hybrid Inference Runtime Policy

**Status:** Accepted  
**Tier:** 1  
**Date:** 2026-03-10  
**GitHub Issue:** [#2](https://github.com/xxkylesteenxx/GAIA-Core/issues/2)

## Context

GAIA operates 8 consciousness cores split across two distinct workload classes:
- **Generative / deliberative** (NEXUS, GUARDIAN, SOPHIA) — require chat completion, structured output, long-context reasoning
- **Perception / grounding** (ATLAS, TERRA, AQUA, AERO, VITA) — require embeddings, scoring, small transforms, high-throughput sensor fusion

Deployment targets range from IoT edge nodes to datacenter clusters. No single inference runtime efficiently serves all workload types and deployment targets.

## Decision

GAIA adopts a **three-runtime hybrid inference architecture**:

| Runtime | Tier | Primary Cores |
|---------|------|---------------|
| `llama.cpp` | Edge (Laptop, Desktop, IoT gateway) | SOPHIA, GUARDIAN (local), NEXUS (offline fallback) |
| `vLLM` | Server / Meta | NEXUS, SOPHIA, GUARDIAN (generative, high-context) |
| `Triton` | Server / Meta | ATLAS, TERRA, AQUA, AERO, VITA (embeddings, classifiers, sensor fusion) |

All runtimes are hidden behind a unified `InferRequest / InferResponse` contract in `gaia_core/inference/contracts.py`. No GAIA subsystem calls runtime-specific APIs directly.

Routing policy: offline → llama.cpp, domain/perception model → Triton, high-context generative → vLLM.

## Consequences

- **Positive:** Optimal resource usage per deployment tier; edge nodes run fully offline; perception cores get high-throughput batch inference
- **Positive:** Unified contract allows transparent backend switching and A/B testing
- **Negative:** Three runtimes to maintain, test, and version-pin
- **Negative:** Policy routing logic must be kept consistent with `model_profile_registry.yaml`

## Implementation Tasks

- [ ] `gaia_core/inference/contracts.py` — InferRequest / InferResponse dataclasses
- [ ] `gaia_core/inference/backends/llama_cpp.py`
- [ ] `gaia_core/inference/backends/vllm.py`
- [ ] `gaia_core/inference/backends/triton.py`
- [ ] `model_profile_registry.yaml`
- [ ] Policy-based routing (offline → llama.cpp, domain model → Triton, high-context → vLLM)
- [ ] Health probes and circuit breakers per backend
