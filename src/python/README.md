# GAIA Python Core Orchestration Pack

This pack provides a Rust- and kernel-compatible Python orchestration layer for the eight GAIA cores.

## Purpose

Python is used here for:
- Abstract core contracts
- Typed state and message models
- Registry / health supervision
- Async message routing
- Planetary state propagation
- Semantic coordination across TERRA, AQUA, AERO, VITA, SOPHIA, GUARDIAN, NEXUS, and ETA

It is **not** intended to be the sole substrate for hard real-time control, strong isolation, or high-throughput numerical kernels. Those concerns are offloaded to lower-level Rust and kernel services.

## Layout

```
gaia_cores/
├── base.py          ← abstract GaiaCore interface
├── models.py        ← CoreMessage, HealthStatus, StateSnapshot
├── bus.py           ← async CoreMessageBus
├── registry.py      ← CoreRegistry — boot, health, snapshot
├── propagation.py   ← planetary state propagation
└── cores/
    ├── terra.py
    ├── aqua.py
    ├── aero.py
    ├── vita.py
    ├── sophia.py
    ├── guardian.py
    ├── nexus.py
    └── eta.py
examples/run_demo.py
tests/test_registry.py
```

## Quick Start

```bash
cd src/python
pip install -e ".[dev]"
python examples/run_demo.py
python -m pytest tests/ -v
```

## Spec Reference

See `docs/specs/PYTHON-ORCHESTRATION-SPEC-v1.0.md`.
