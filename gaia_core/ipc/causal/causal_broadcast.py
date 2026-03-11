"""Causal broadcast with holdback queue.

Guarantees causal delivery ordering:
  A message M is deliverable only when all messages that causally
  precede M have already been delivered.

Holdback: messages whose causal dependencies are unsatisfied
are buffered until predecessors arrive.

Broadcast classes:
  causal.broadcast.control   — NEXUS/GUARDIAN state
  causal.broadcast.memory    — memory consolidation
  causal.broadcast.policy    — policy propagation
  causal.broadcast.health    — health/failover beacons

High-volume telemetry does NOT require causal ordering.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Callable

from gaia_core.models import VectorClock
from gaia_core.ipc.contracts import GaiaEnvelope

log = logging.getLogger(__name__)

BROADCAST_CLASSES = [
    "causal.broadcast.control",
    "causal.broadcast.memory",
    "causal.broadcast.policy",
    "causal.broadcast.health",
]

DeliverFn = Callable[[GaiaEnvelope], None]


@dataclass
class _Pending:
    envelope: GaiaEnvelope
    expected_clocks: dict[str, int]  # the sender's clock at send time


class CausalBroadcast:
    """Causal broadcast layer for a single GAIA node.

    Usage:
        cb = CausalBroadcast(node_id="nexus-01", on_deliver=handle_msg)
        cb.receive(envelope)   # called on every incoming message
        cb.send(envelope)      # stamps and queues for local delivery
    """

    def __init__(
        self,
        node_id: str,
        on_deliver: DeliverFn | None = None,
    ) -> None:
        self.node_id = node_id
        self._on_deliver = on_deliver or (lambda _: None)
        # Per-sender, last delivered vector clock component
        self._delivered: dict[str, int] = defaultdict(int)
        self._holdback: list[_Pending] = []
        self._lock = Lock()

    def send(self, envelope: GaiaEnvelope) -> GaiaEnvelope:
        """Prepare an outgoing envelope (caller is responsible for transport)."""
        # Delivery to self is immediate
        self._deliver(envelope)
        return envelope

    def receive(self, envelope: GaiaEnvelope) -> list[GaiaEnvelope]:
        """Process an incoming envelope. Returns list of newly delivered envelopes."""
        with self._lock:
            if self._can_deliver(envelope):
                return self._deliver_chain(envelope)
            else:
                log.debug(
                    "Holding back message %s from %s (causal deps unsatisfied)",
                    envelope.message_id, envelope.source_core,
                )
                self._holdback.append(_Pending(
                    envelope=envelope,
                    expected_clocks=dict(envelope.causal_clock),
                ))
                return []

    def _can_deliver(self, envelope: GaiaEnvelope) -> bool:
        """A message is deliverable when its causal clock is consistent with delivered state."""
        sender = envelope.source_core
        clock = envelope.causal_clock
        if not clock:
            return True  # no clock = always deliverable (e.g. query messages)
        # Sender's own counter must be exactly next expected
        sender_count = clock.get(sender, 0)
        if sender_count != self._delivered[sender] + 1:
            return False
        # All other dimensions must be <= our delivered knowledge
        for node, count in clock.items():
            if node == sender:
                continue
            if count > self._delivered[node]:
                return False
        return True

    def _deliver_chain(self, envelope: GaiaEnvelope) -> list[GaiaEnvelope]:
        """Deliver and cascade to any newly unblocked holdback messages."""
        delivered = [envelope]
        sender = envelope.source_core
        self._delivered[sender] = envelope.causal_clock.get(sender, self._delivered[sender] + 1)
        self._on_deliver(envelope)

        # Check holdback for newly deliverable messages
        released = True
        while released:
            released = False
            still_held = []
            for pending in self._holdback:
                if self._can_deliver(pending.envelope):
                    delivered.extend(self._deliver_chain(pending.envelope))
                    released = True
                else:
                    still_held.append(pending)
            self._holdback = still_held

        return delivered

    def _deliver(self, envelope: GaiaEnvelope) -> None:
        """Local send — always deliverable."""
        sender = envelope.source_core
        self._delivered[sender] = max(
            self._delivered[sender],
            envelope.causal_clock.get(sender, 0),
        )
        self._on_deliver(envelope)

    def holdback_depth(self) -> int:
        with self._lock:
            return len(self._holdback)

    def delivered_summary(self) -> dict[str, int]:
        with self._lock:
            return dict(self._delivered)
