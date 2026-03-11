"""NexusSyncService — gRPC cross-core coherence synchronisation stub.

Handles:
  - CoherenceBarrier: synchronise generation counters across NEXUS instances
  - StateSnapshot: push/pull coherence state snapshots
  - HealthBeacon: liveness and degraded-mode signalling

This is a stub that defines the service interface and data contracts.
Real gRPC transport wiring requires a generated Protobuf client
(see gaia_core/ipc/proto/nexus/ for schema definitions).

The stub is runnable in-process for testing and local multi-core operation.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Callable

from gaia_core.ipc.contracts import GaiaEnvelope, DataClass, MessagePriority

log = logging.getLogger(__name__)


@dataclass
class CoherenceBarrierRequest:
    source_core: str
    generation: int
    vector_clock: dict[str, int]
    trace_id: str = ""


@dataclass
class CoherenceBarrierResponse:
    accepted: bool
    generation: int
    merged_clock: dict[str, int]
    latency_ms: float = 0.0
    detail: str = ""


@dataclass
class HealthBeacon:
    node_id: str
    core: str
    timestamp_ns: int = field(default_factory=time.monotonic_ns)
    degraded: bool = False
    risk_level: str = "green"  # green | yellow | red | black
    detail: str = ""


class NexusSyncService:
    """In-process NexusSyncService stub.

    Replace with gRPC-generated client for cross-host operation.
    """

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self._generation: int = 0
        self._clock: dict[str, int] = {}
        self._beacon_handlers: list[Callable[[HealthBeacon], None]] = []

    def barrier(self, req: CoherenceBarrierRequest) -> CoherenceBarrierResponse:
        """Process a coherence barrier request. Merges clocks and advances generation."""
        t0 = time.monotonic()
        # Merge incoming vector clock
        for node, count in req.vector_clock.items():
            self._clock[node] = max(self._clock.get(node, 0), count)
        # Accept if generation is >= our current (idempotent)
        if req.generation >= self._generation:
            self._generation = req.generation
            accepted = True
        else:
            accepted = False
            log.warning(
                "NexusSync: barrier rejected stale generation %d (current=%d)",
                req.generation, self._generation,
            )
        latency_ms = (time.monotonic() - t0) * 1000
        return CoherenceBarrierResponse(
            accepted=accepted,
            generation=self._generation,
            merged_clock=dict(self._clock),
            latency_ms=latency_ms,
        )

    def emit_beacon(self, beacon: HealthBeacon) -> None:
        """Emit a health beacon to all registered handlers."""
        log.info(
            "HealthBeacon: node=%s core=%s risk=%s degraded=%s",
            beacon.node_id, beacon.core, beacon.risk_level, beacon.degraded,
        )
        for handler in self._beacon_handlers:
            handler(beacon)

    def on_beacon(self, handler: Callable[[HealthBeacon], None]) -> None:
        """Register a handler for incoming health beacons."""
        self._beacon_handlers.append(handler)

    def to_envelope(self, payload: dict[str, Any]) -> GaiaEnvelope:
        """Wrap a NexusSync payload in a Class A GaiaEnvelope."""
        return GaiaEnvelope(
            source_core="NEXUS",
            target_core="NEXUS",
            payload=payload,
            data_class=DataClass.A,
            priority=MessagePriority.CRITICAL,
            causal_clock=dict(self._clock),
        )
