# ADR-002: Storage Substrate

**Status:** Accepted  
**Tier:** 1  
**Date:** 2026-03-10  
**GitHub Issue:** [#3](https://github.com/xxkylesteenxx/GAIA-Core/issues/3)

## Context

GAIA requires durable, distributed storage across three distinct access patterns:
- **Object storage** — large blobs (checkpoints, evidence bundles, model manifests, observation batches)
- **Consistent metadata / coordination** — small values needing linearizable reads (node registry, continuity head pointers, leases, leader election)
- **Causal event streaming / WAL** — ordered, replayable event log for consciousness state changes, actions, and sensor fan-in

No single database efficiently serves all three patterns.

## Decision

GAIA adopts a **three-part storage substrate**:

| System | Role | GAIA Usage |
|--------|------|------------|
| `MinIO` | Durable object store | Checkpoints, evidence bundles, model manifests, observation batches, digital twin exports |
| `etcd` | Consistent metadata + coordination | Node registry, continuity head pointers, leases, runtime routing, leader election |
| `NATS JetStream` | Causal WAL + event streaming | Causal memory log, action proposals, Guardian decisions, sensor fan-in, replay substrate |

**WAL write pattern:**
1. Write event to JetStream (durable commit)
2. Async materialize to MinIO
3. Record head/lease in etcd

## Consequences

- **Positive:** Each system is best-in-class for its access pattern; clean separation of concerns
- **Positive:** JetStream causal log enables full replay-based restore — foundation for Tier 2 cross-host continuity
- **Negative:** Three infra services to operate; local dev requires Docker Compose or equivalent
- **Negative:** WAL → MinIO async path requires careful error handling to avoid checkpoint drift

## Implementation Tasks

- [ ] `gaia_core/storage/__init__.py`
- [ ] `gaia_core/storage/minio_store.py`
- [ ] `gaia_core/storage/jetstream_log.py`
- [ ] `gaia_core/storage/etcd_registry.py`
- [ ] Object naming conventions + digest/signature metadata on every checkpoint
- [ ] Replay bootstrap (JetStream → reconstruct continuity head → restore checkpoint)
- [ ] `deploy/local/docker-compose.infra.yaml` (MinIO + etcd + NATS)
