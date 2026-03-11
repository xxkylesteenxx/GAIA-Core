"""IPC observability — metrics and instrumentation hooks.

Tracks:
  - ring occupancy per MemfdRing
  - causal holdback queue depth
  - vector-clock conflict count
  - out-of-order arrival count
  - fallback path activation count
  - gRPC-equivalent call latency per service method
"""
from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock

log = logging.getLogger(__name__)


@dataclass
class RingMetrics:
    name: str
    capacity: int
    used: int = 0
    total_put: int = 0
    total_get: int = 0
    dropped: int = 0


@dataclass
class CausalMetrics:
    holdback_depth: int = 0
    total_delivered: int = 0
    total_held: int = 0
    out_of_order_arrivals: int = 0
    clock_conflicts: int = 0


@dataclass
class ServiceLatency:
    method: str
    call_count: int = 0
    total_ms: float = 0.0
    min_ms: float = float("inf")
    max_ms: float = 0.0

    def record(self, ms: float) -> None:
        self.call_count += 1
        self.total_ms += ms
        self.min_ms = min(self.min_ms, ms)
        self.max_ms = max(self.max_ms, ms)

    @property
    def avg_ms(self) -> float:
        return self.total_ms / self.call_count if self.call_count else 0.0


class IpcObservability:
    """Central IPC metrics registry."""

    def __init__(self) -> None:
        self._rings: dict[str, RingMetrics] = {}
        self._causal = CausalMetrics()
        self._latencies: dict[str, ServiceLatency] = defaultdict(
            lambda: ServiceLatency(method="unknown")
        )
        self._lock = Lock()
        self._fallback_activations: int = 0

    # --- Ring metrics ---
    def register_ring(self, name: str, capacity: int) -> None:
        with self._lock:
            self._rings[name] = RingMetrics(name=name, capacity=capacity)

    def record_ring_put(self, name: str, dropped: bool = False) -> None:
        with self._lock:
            r = self._rings.get(name)
            if r:
                if dropped:
                    r.dropped += 1
                else:
                    r.total_put += 1

    def record_ring_get(self, name: str) -> None:
        with self._lock:
            r = self._rings.get(name)
            if r:
                r.total_get += 1

    def update_ring_occupancy(self, name: str, used: int) -> None:
        with self._lock:
            r = self._rings.get(name)
            if r:
                r.used = used

    # --- Causal metrics ---
    def record_holdback(self) -> None:
        with self._lock:
            self._causal.total_held += 1
            self._causal.out_of_order_arrivals += 1

    def record_delivery(self) -> None:
        with self._lock:
            self._causal.total_delivered += 1

    def update_holdback_depth(self, depth: int) -> None:
        with self._lock:
            self._causal.holdback_depth = depth

    def record_clock_conflict(self) -> None:
        with self._lock:
            self._causal.clock_conflicts += 1

    def record_fallback(self) -> None:
        with self._lock:
            self._fallback_activations += 1

    # --- Service latency ---
    def record_latency(self, method: str, ms: float) -> None:
        with self._lock:
            if method not in self._latencies:
                self._latencies[method] = ServiceLatency(method=method)
            self._latencies[method].record(ms)

    # --- Snapshot ---
    def snapshot(self) -> dict:
        with self._lock:
            return {
                "rings": {n: vars(r) for n, r in self._rings.items()},
                "causal": vars(self._causal),
                "service_latencies": {
                    m: {
                        "calls": l.call_count,
                        "avg_ms": round(l.avg_ms, 3),
                        "min_ms": round(l.min_ms, 3) if l.call_count else None,
                        "max_ms": round(l.max_ms, 3),
                    }
                    for m, l in self._latencies.items()
                },
                "fallback_activations": self._fallback_activations,
            }
