# GAIA Inter-Process Communication Specification v1.0

**Status:** Repo-ready architecture specification  
**Recommended path:** `GAIA-Core/platform/ipc/docs/GAIA_Inter_Process_Communication_Spec_v1.0.md`  
**Scope:** zero-copy local IPC, asynchronous I/O, gRPC/Protobuf contracts, causal broadcast ordering  
**Primary objective:** Create a transport stack that supports fast local coordination, typed cross-core contracts, and causally sane distributed state propagation.

---

## 1. Executive Position

GAIA should use a **three-tier IPC fabric**:

1. **Local fast path:** `memfd` + shared memory rings + eventfd/futex
2. **Host async transport:** `io_uring` for file, socket, and queue operations
3. **Networked contract plane:** gRPC with Protobuf schemas, wrapped in causal metadata for cross-core ordering

Do **not** force one mechanism to solve every problem.

---

## 2. Research-grounded conclusions

### 2.1 `memfd_create()` is the right primitive for local zero-copy state exchange
`memfd_create()` creates anonymous RAM-backed files that can be truncated, memory mapped, and sealed. For GAIA this is ideal for:
- hot shared buffers
- ring queues
- snapshot exchange
- immutable handoff via seals
- crash-tolerant inherited mappings

### 2.2 `io_uring` should be the async I/O engine
`io_uring` is Linux's shared-ring asynchronous I/O facility. GAIA should use it for:
- socket ingress/egress
- WAL and audit log append
- spill-to-disk snapshots
- remote memory fetches
- backpressure-aware bulk transfer

### 2.3 gRPC + Protobuf is the contract plane, not the hot-path ring
GAIA should use gRPC/Protobuf for:
- typed cross-core requests
- operator APIs
- remote procedure orchestration
- inter-host core contract enforcement
- portable tracing and observability

### 2.4 causal ordering must be explicit
Cross-core messages that change shared state must include explicit causal metadata. Vector clocks remain the most straightforward exact mechanism for small, mostly stable process sets.

---

## 3. IPC architecture

### 3.1 Transport layers
```text
L0  In-process: lock-free queues / channels
L1  Same-host hot path: memfd shared rings + eventfd/futex
L2  Same-host async service path: Unix domain sockets + io_uring
L3  Cross-host control/data path: gRPC + Protobuf over mTLS / PQC transport
L4  Distributed state propagation: causal broadcast envelope with vector clocks
```

### 3.2 Data classes

**Class A — coherence critical**
- NEXUS barrier state, GUARDIAN veto, coherence generation updates, health/failover beacons

**Class B — sensor and memory streaming**
- environmental observation windows, retrieval results, fused state vectors, causal snapshots

**Class C — bulk and archival**
- replay logs, training exports, forensic captures, historical reindex streams

---

## 4. gRPC / Protobuf contract layer

### Base message
```proto
message GaiaEnvelope {
  string message_id = 1;
  string source_core = 2;
  string target_core = 3;
  uint64 monotonic_ns = 4;
  string trace_id = 5;
  bytes causal_clock = 6;
  string contract_version = 7;
  bytes auth_context = 8;
}
```

---

## 5. Bottom line

GAIA should use **`memfd` for same-host zero-copy exchange, `io_uring` for async I/O execution, and gRPC/Protobuf for typed cross-core contracts**, with **causal broadcast and vector clocks** on any distributed state path that must preserve dependency order.
