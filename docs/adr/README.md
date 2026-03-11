# Architecture Decision Records (ADRs)

This directory contains the Architecture Decision Records for GAIA-Core.

ADRs document significant design decisions, their rationale, and the consequences
of those decisions. Each ADR is also tracked as a GitHub Issue with labels
`adr`, `tier-N`, and the relevant domain.

## Index

| ADR | Title | Status | Tier | Issue |
|-----|-------|--------|------|-------|
| [ADR-001](ADR-001-hybrid-inference-runtime.md) | Hybrid Inference Runtime Policy (llama.cpp + vLLM + Triton) | Accepted | 1 | [#2](https://github.com/xxkylesteenxx/GAIA-Core/issues/2) |
| [ADR-002](ADR-002-storage-substrate.md) | Storage Substrate (MinIO + etcd + NATS JetStream) | Accepted | 1 | [#3](https://github.com/xxkylesteenxx/GAIA-Core/issues/3) |
| [ADR-003](ADR-003-tpm-attestation.md) | TPM 2.0 Identity Attestation | Draft | 1 | TBD |
| [ADR-004](ADR-004-earth-system-connectors.md) | Earth-System Data Connectors (NOAA, USGS, GBIF, iNaturalist) | Draft | 1 | TBD |
| [ADR-005](ADR-005-cross-host-restore.md) | Cross-Host Consciousness Restore | Draft | 2 | TBD |
| [ADR-006](ADR-006-jurisdiction-engine.md) | OPA Jurisdiction Engine | Draft | 2 | TBD |
| [ADR-007](ADR-007-federation-spiffe.md) | SPIFFE/SVID Secure Federation | Draft | 2 | TBD |
| [ADR-008](ADR-008-merge-governance-crdt.md) | CRDT Merge Governance | Draft | 2 | TBD |

## Format

Each ADR file follows this structure:

```
# ADR-NNN: Title
**Status:** Draft | Accepted | Deprecated | Superseded
**Tier:** 1 | 2 | 3
**Date:** YYYY-MM-DD
**GitHub Issue:** #N

## Context
## Decision
## Consequences
## Implementation Tasks
```

## Contributing

To propose a new ADR:
1. Create a GitHub Issue with labels `adr` + `tier-N` + domain
2. Copy the template above into a new `ADR-NNN-title.md` file
3. Open a PR referencing the issue
