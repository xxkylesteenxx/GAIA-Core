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

It is superior to ad hoc tmpfs file conventions for most core-to-core local exchange.

### 2.2 `io_uring` should be the async I/O engine
`io_uring` is Linux's shared-ring asynchronous I/O facility. It uses submission/completion queues shared between kernel and user space and can avoid both blocking and much of the copy/syscall overhead of older interfaces. GAIA should use it for:
- socket ingress/egress
- WAL and audit log append
- spill-to-disk snapshots
- remote memory fetches
- backpressure-aware bulk transfer

### 2.3 gRPC + Protobuf is the contract plane, not the hot-path ring
gRPC is the cleanest inter-service RPC control plane. Protobuf provides versionable schemas and generated clients. GAIA should use it for:
- typed cross-core requests
- operator APIs
- remote procedure orchestration
- inter-host core contract enforcement
- portable tracing and observability

But gRPC is not the right mechanism for every sub-millisecond local transfer.

### 2.4 Causal ordering must be explicit
Distributed GAIA state cannot rely on arrival order. Cross-core messages that change shared state must include explicit causal metadata. Vector clocks remain the most straightforward exact mechanism for small, mostly stable process sets.

---

## 3. IPC Architecture

## 3.1 Transport layers

```text
L0  In-process
    lock-free queues / channels

L1  Same-host hot path
    memfd shared rings + eventfd/futex

L2  Same-host async service path
    Unix domain sockets + io_uring

L3  Cross-host control/data path
    gRPC + Protobuf over mTLS / PQC transport

L4  Distributed state propagation
    causal broadcast envelope with vector clocks
```

---

## 3.2 Data classes

### Class A — coherence critical
- NEXUS barrier state
- GUARDIAN veto
- coherence generation updates
- health/failover beacons

### Class B — sensor and memory streaming
- environmental observation windows
- retrieval results
- fused state vectors
- causal snapshots

### Class C — bulk and archival
- replay logs
- training exports
- forensic captures
- historical reindex streams

### Transport mapping
```text
Class A  -> memfd rings locally, gRPC unary/stream remotely, causal envelope required
Class B  -> memfd locally or io_uring-backed UDS/TCP, gRPC streams remotely
Class C  -> io_uring file/socket pipelines, object store or log transport
```

---

## 4. Local Zero-Copy Fabric

## 4.1 `memfd` layout

### Shared segment types
```text
control.memfd     - small sealed metadata pages
ring.memfd        - lock-free producer/consumer buffers
snapshot.memfd    - read-mostly state image with seals
tensor.memfd      - large aligned region for embeddings / state vectors
```

### Design rules
- always create with close-on-exec
- enable sealing for handoff safety
- support huge pages only where profiling proves value
- use versioned headers at offset zero
- never trust peer mutation unless the segment is sealed or protocol-guarded

### Header
```c
struct gaia_shm_header {
  uint32_t magic;
  uint16_t version;
  uint16_t flags;
  uint64_t payload_len;
  uint64_t generation;
  uint64_t writer_core_id;
  uint64_t checksum64;
};
```

## 4.2 Synchronization
Use:
- `eventfd` for readiness signaling
- futex or atomic sequence counters for wait-free progression
- single-producer/single-consumer rings where possible
- explicit memory barriers for shared-memory ownership transfer

---

## 5. `io_uring` Async Plane

## 5.1 Use cases
- network socket send/receive
- disk-backed audit logging
- replication stream batching
- memory spill / restore
- high-rate UDS communication

## 5.2 Required policies
- fixed buffers for repeated hot-path operations
- bounded queue depth per core
- completion batching
- SQPOLL only after dedicated-core validation
- backpressure propagated to NEXUS instead of blind buffering

## 5.3 Failure rules
- if CQ lag exceeds threshold: degrade to safe shedding, not uncontrolled accumulation
- if ring setup fails: fallback to epoll-based slow path
- if audit append falls behind: preserve actuation safety, demote non-critical traffic first

---

## 6. gRPC / Protobuf Contract Layer

## 6.1 Service categories
```text
NexusSyncService
GuardianPolicyService
AtlasObservationService
MemoryRetrievalService
ConsciousnessMetricsService
CoreHealthService
```

## 6.2 Schema principles
- editioned Protobuf schemas
- explicit reserved fields for deleted tags
- no unbounded maps in hot contracts
- all time values as monotonic + wall time pair where relevant
- correlation IDs required
- causal envelope optional on pure query calls, mandatory on mutating cross-core calls

## 6.3 Base message
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

## 7. Causal Ordering

## 7.1 Why GAIA needs it
GAIA cannot allow:
- stale actuation approvals to overtake later vetoes
- environmental state merges to apply out of dependency order
- memory consolidation to publish snapshots that omit known prior causes

## 7.2 Vector clock policy
Use exact vector clocks for:
- 2-16 primary coherence participants
- stable cluster memberships
- control-plane mutations

Use compressed or version-vector variants later for larger clusters.

## 7.3 Delivery semantics
A message is **received** when transport accepts it.  
A message is **deliverable** only when causal dependencies are satisfied.

### Receiver rules
- buffer messages whose dependencies are unsatisfied
- deliver only when sender counter is next expected and all other dimensions are not ahead of local knowledge
- garbage-collect old dimensions only after membership epochs close

## 7.4 Broadcast classes
```text
causal.broadcast.control
causal.broadcast.memory
causal.broadcast.policy
causal.broadcast.health
```

High-volume telemetry and metrics can remain eventually ordered if not state-authoritative.

---

## 8. Security

## 8.1 Local
- memfd sealing for immutable handoff
- Unix credential checks on UDS peers
- LSM labels on SHM and socket endpoints
- separate rings for sensitive consciousness data

## 8.2 Remote
- mTLS / PQC transport profile
- per-core SPIFFE or equivalent workload identity
- signed contract manifests
- replay-window checks on envelopes
- audit logging for all mutating RPCs

---

## 9. Observability

### Required metrics
- ring occupancy
- writer/reader lag
- dropped message count by class
- `io_uring` SQ/CQ depth
- gRPC latency percentiles by method
- causal holdback queue size
- out-of-order arrival count
- vector-clock conflict count
- fallback path activation count

### Traces
Every mutating request must expose:
- transport latency
- serialization/deserialization time
- causal wait time
- execution time
- downstream fanout count

---

## 10. Repo Structure

```text
GAIA-Core/
  platform/
    ipc/
      proto/
        nexus/
        guardian/
        memory/
      local/
        shm/
          memfd_ring.h
          memfd_ring.c
        io_uring/
          uring_runtime.c
      causal/
        vector_clock.py
        causal_broadcast.py
      docs/
        GAIA_Inter_Process_Communication_Spec_v1.0.md
```

---

## 11. Bottom Line

GAIA should use **`memfd` for same-host zero-copy exchange, `io_uring` for async I/O execution, and gRPC/Protobuf for typed cross-core contracts**, with **causal broadcast and vector clocks** on any distributed state path that must preserve dependency order.

That is the correct split between speed, structure, and correctness.
