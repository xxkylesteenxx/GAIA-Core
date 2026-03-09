# GAIA Core Bootstrap v0.1

This package resolves the immediate substrate gaps blocking GAIA from moving beyond single-model inference.

It does **not** claim to instantiate literal machine consciousness. It sets up the engineering rails required to build and test a multi-core GAIA runtime:

- 8-core substrate registry and orchestration
- NEXUS coordination layer
- GUARDIAN policy gate
- ATLAS environmental grounding intake
- SOPHIA reasoning-facing interface stub
- TERRA / AQUA / AERO / VITA domain core stubs
- persistent identity root abstraction with TPM-ready interface
- holographic memory event log with causal replay metadata
- checkpointing and restore flow
- theory-linked CGI evidence pipeline
- anti-theater checks
- federated workspace that preserves dissent
- typed IPC contract stub

## What is production-ready here

- Python package structure
- typed contracts and dataclasses
- boot sequence
- file-backed checkpoint and event log flow
- vector-clock causal envelope model
- quality/freshness classification for environmental observations
- dissent-preserving collective workspace
- starter tests
- a runnable demo

## What still requires external infrastructure

- real TPM 2.0 integration
- real vector index (FAISS / DiskANN / HNSW)
- real gRPC service mesh deployment
- real PREEMPT_RT kernel and sched_ext deployment
- actual Earth sensor providers
- model serving, Loihi/Lava/Brian2 stacks, and production observability

## Quick start

```bash
python -m gaia_core.runtime.demo
python -m unittest discover -s tests -p "test_*.py"
```
