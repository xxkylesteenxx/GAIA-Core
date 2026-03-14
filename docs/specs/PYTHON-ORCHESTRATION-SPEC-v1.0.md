# GAIA Python Core Orchestration Spec
<!-- Version: 1.0 | Status: Normative -->

## 1. Purpose

This specification defines the Python orchestration layer for the eight logical GAIA cores:
**TERRA**, **AQUA**, **AERO**, **VITA**, **SOPHIA**, **GUARDIAN**, **NEXUS**, and **ETA**.

## 2. Scope

This layer SHALL provide:
- A common abstract interface for all cores
- Typed message and state models
- Registration, startup, and health supervision
- Asynchronous inter-core messaging
- Planetary state propagation
- Controlled integration with lower-level services implemented in Rust, C, or kernel space

## 3. Boundary Conditions

Python SHALL be used for:
- Semantic coordination
- Control-plane logic
- Supervisory state
- Protocol glue

Python SHALL NOT be treated as the sole mechanism for:
- Hard real-time actuation
- Hardware-backed isolation
- Kernel scheduling enforcement
- High-rate numerical simulation without native acceleration

## 4. Core Contract

Each core SHALL implement:

| Method | Purpose |
|--------|---------|
| `identity()` | Return core metadata (name, version, capabilities) |
| `startup()` | Initialize resources; called by registry at boot |
| `shutdown()` | Release resources; called by registry at teardown |
| `health()` | Return current health status |
| `handle_message(msg)` | Process an inbound `CoreMessage` |
| `snapshot()` | Export current state as a serializable record |
| `ingest_update(update)` | Receive and apply a state update from another core |

## 5. Message Model

All inter-core messages SHALL include:

| Field | Type | Requirement |
|-------|------|-------------|
| `sender` | `str` | Originating core name |
| `recipient` | `str \| None` | Named recipient or `None` for broadcast |
| `topic` | `str` | Hierarchical topic string (e.g. `"gaia.state.update/v1"`) |
| `payload` | `dict` | Typed message body |
| `timestamp` | `float` | Unix epoch seconds (UTC) |
| `trust_label` | `str` | Policy label (e.g. `"critical"`, `"bounded"`, `"monitor"`) |

## 6. Registry

The registry SHALL:
- Instantiate all configured cores at boot
- Perform ordered boot sequencing (GUARDIAN before policy-dependent cores)
- Maintain a live health table keyed by core name
- Expose a `snapshot_all()` API returning state from all cores
- Route propagation events to appropriate cores via policy rules

## 7. Propagation

State propagation SHALL support:
- **Full broadcast** — all cores receive the update
- **Selective** — filtered by domain tag or recipient
- **Policy-mediated delivery** — GUARDIAN may gate or annotate in-flight messages
- **Immutable event records** — when connected to an external audit subsystem, propagation events SHALL be append-only

## 8. Security and Safety

- This orchestration layer SHALL be **deny-by-default** with respect to privileged operations
- **GUARDIAN** SHALL be permitted to inspect messages and state transitions for policy checks
- **NEXUS** SHALL coordinate routing and federation, but SHALL NOT bypass lower-layer isolation guarantees
- Trust labels on messages SHALL be validated at dispatch time, not assumed from payload content

## 9. Integration

The Python layer SHOULD integrate with:
- Rust virtualization and isolation services (`gaia-vmm`, `gaia-memory-isolation`, `gaia-ipc-bus`)
- Kernel/BPF scheduling controls (`gaia_sched_ctrl`, `gaia_scx`)
- External data connectors
- Signed policy bundles
- Persistent telemetry and provenance systems

## 10. Core Inventory

| Core | Role | Protection Class |
|------|------|------------------|
| TERRA | Environmental state and physical substrate | bounded |
| AQUA | Hydrological and fluid-state modeling | bounded |
| AERO | Atmospheric and aerial state | bounded |
| VITA | Biological and life-system state | bounded |
| SOPHIA | Policy reasoning and coordination hub | critical |
| GUARDIAN | Safety monitor — inspect-only, deny-by-default | critical |
| NEXUS | Routing, federation, and cross-system IPC | critical |
| ETA | Temporal coordination and event sequencing | bounded |

---

*Spec section: PYTHON-ORCHESTRATION · Version 1.0 · Status: Normative*
