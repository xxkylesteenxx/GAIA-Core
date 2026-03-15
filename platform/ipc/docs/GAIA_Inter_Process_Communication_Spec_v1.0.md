# GAIA Inter-Process Communication Spec v1.0

## Status
Draft v1.0

## Purpose
This specification defines the local inter-process communication substrate for GAIA workloads that must exchange state with low overhead, deterministic ordering semantics, and explicit security/policy hooks. The IPC stack is split into four layers:

1. **Local zero-copy shared memory plane** for high-rate same-host exchange.
2. **io_uring asynchronous plane** for event-driven local I/O and broker integration.
3. **Protocol contracts** expressed in Protocol Buffers for typed cross-core messages.
4. **Causal ordering layer** for concurrency-aware, replayable coordination semantics.

## Design goals
- Prefer same-host zero-copy paths before kernel TCP loopback.
- Support policy-bound coordination across GAIA cores such as NEXUS and GUARDIAN.
- Make message semantics explicit and versionable.
- Preserve causal relationships where total ordering is unnecessary or too costly.
- Keep transport and semantics separable.

## Layer 1: memfd shared-memory ring
The `memfd_ring` implementation provides a fixed-slot shared-memory ring backed by `memfd_create(2)` so the ring can be sealed, mapped into multiple processes, and passed over Unix domain sockets using `SCM_RIGHTS`. Slots are fixed-size to avoid allocator interaction on the hot path.

### Operational contract
- Metadata lives at the start of the mapping.
- Producers claim a slot, write in place, then commit with a publish fence.
- Consumers read a slot view, process, then commit release.
- Backpressure is explicit: a full ring returns `EAGAIN` and increments overrun counters.

## Layer 2: io_uring runtime
`uring_runtime.c` provides a minimal same-process runtime wrapper around `liburing`. GAIA brokers or bridge daemons can use it to multiplex pipe, socket, or file events without a thread-per-connection model.

## Layer 3: Protocol contracts
The protobuf contracts included here define:
- **NEXUS sync** envelopes and acknowledgements.
- **GUARDIAN policy** requests and decisions.
- **Memory retrieval** requests for retrieval-augmented subsystems.

## Layer 4: Causal ordering
Vector clocks are used where full consensus is not required but reordering would corrupt reasoning or state reconciliation. The causal broadcaster delivers a message only when its predecessor conditions are satisfied.

## Security and trust boundaries
- Shared memory is same-host only and must not cross host boundaries without explicit serialization.
- Ring file descriptors must be distributed only over authenticated Unix domain channels.
- High-trust topics (e.g., `guardian.policy`) should combine transport-level authorization with payload-level signatures.
- Causal metadata is advisory for ordering, not an authorization primitive.

## Observability
Implementations SHOULD expose at minimum:
- ring depth
- ring overruns / drops
- queueing delay
- pending causal backlog
- message size distributions by topic

## Compatibility
This spec is intentionally narrow. Cross-host transport, consensus replication, and durable event logs belong in higher-layer GAIA messaging specifications.
