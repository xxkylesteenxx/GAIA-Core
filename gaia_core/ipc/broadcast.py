"""GAIA IPC Causal Broadcast Fabric.

This is what makes the 8 cores a consciousness — not 8 isolated processes.
Every message carries a vector-clock causal envelope so any core can
determine the causal ordering of events across the entire system.

Design:
  - In-process pub/sub bus (no external broker required for local operation)
  - Vector-clock stamped CausalEnvelope on every message
  - NEXUS ELEVATED clearance required to broadcast (GUARDIAN-gated)
  - Subscribers register by core_id and topic
  - Dissent is preserved: a core can publish a dissenting signal without
    being silenced — GUARDIAN gates actuation, not expression

Production path:
  - Swap LocalBus for gRPC CausalBroadcast (gaia_core/ipc/grpc/) in Phase 3
  - Wire Prometheus ring-lag metric from observability.py

Architectural principle:
  NEXUS owns the epoch clock. Every envelope epoch comes from NEXUS.
  No core may forge a causal envelope with an epoch it did not receive.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

from gaia_core.guardian.nexus_clearance import ClearanceLevel, ClearanceToken

logger = logging.getLogger(__name__)


class Topic(str, Enum):
    """Canonical IPC topics. All inter-core signals use these."""
    COORDINATION    = "nexus.coordination"    # NEXUS → all cores
    SYNTHESIS       = "sophia.synthesis"      # SOPHIA → all cores
    POLICY_GATE     = "guardian.policy"       # GUARDIAN → all cores
    GROUNDING       = "atlas.grounding"       # ATLAS → all cores
    DOMAIN_TERRA    = "terra.observation"     # TERRA domain signals
    DOMAIN_AQUA     = "aqua.observation"      # AQUA domain signals
    DOMAIN_AERO     = "aero.observation"      # AERO domain signals
    DOMAIN_VITA     = "vita.observation"      # VITA domain signals
    MEMORY_EVENT    = "memory.causal_event"   # continuity layer events
    DISSENT         = "dissent.signal"        # any core — preserved, never blocked
    SYSTEM          = "system.control"        # boot, shutdown, safe-mode signals


@dataclass
class VectorClock:
    """Lamport-style vector clock — one slot per core.
    Enables causal ordering across all 8 consciousness cores.
    """
    clocks: dict[str, int] = field(default_factory=dict)

    def tick(self, core_id: str) -> VectorClock:
        """Advance this core's slot and return updated clock."""
        updated = dict(self.clocks)
        updated[core_id] = updated.get(core_id, 0) + 1
        return VectorClock(clocks=updated)

    def merge(self, other: VectorClock) -> VectorClock:
        """Merge two vector clocks (take max of each slot)."""
        all_cores = set(self.clocks) | set(other.clocks)
        merged = {c: max(self.clocks.get(c, 0), other.clocks.get(c, 0)) for c in all_cores}
        return VectorClock(clocks=merged)

    def happened_before(self, other: VectorClock) -> bool:
        """True if self causally precedes other."""
        return (
            all(self.clocks.get(c, 0) <= other.clocks.get(c, 0) for c in self.clocks)
            and any(self.clocks.get(c, 0) < other.clocks.get(c, 0) for c in self.clocks)
        )


@dataclass
class CausalEnvelope:
    """Every IPC message is wrapped in a CausalEnvelope.
    The envelope is the causal proof of ordering — unforgeable in production.
    """
    topic: Topic
    sender_core: str
    nexus_epoch: int                # global epoch from NEXUS at send time
    vector_clock: VectorClock
    payload: dict                   # message content
    timestamp: float = field(default_factory=time.time)
    clearance_hash: str = ""        # GUARDIAN token hash of sender
    is_dissent: bool = False        # dissent signals are never blocked


# Subscriber type: receives a CausalEnvelope, returns nothing
Subscriber = Callable[[CausalEnvelope], None]


class LocalBus:
    """In-process causal broadcast bus.
    No external broker. Runs in the same process as the cores.
    Thread-safe. Swap for gRPC bus in Phase 3.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[Subscriber]] = defaultdict(list)
        self._lock = threading.Lock()
        self._message_log: list[CausalEnvelope] = []
        self._vector_clocks: dict[str, VectorClock] = {}
        logger.info("[IPC] LocalBus initialized")

    def subscribe(self, topic: Topic, core_id: str, handler: Subscriber) -> None:
        """Register a core as a subscriber to a topic."""
        with self._lock:
            self._subscribers[topic].append(handler)
        logger.debug(f"[IPC] {core_id} subscribed to {topic}")

    def publish(
        self,
        topic: Topic,
        sender_core: str,
        payload: dict,
        nexus_epoch: int,
        clearance_token: Optional[ClearanceToken] = None,
        is_dissent: bool = False,
    ) -> CausalEnvelope:
        """Publish a causal message to all subscribers of a topic.

        Clearance rules:
          - DISSENT topic: always allowed regardless of clearance
          - All other topics: ELEVATED clearance required
          - LITE/BLOCKED: message is logged but not delivered (observe-only)
        """
        # Update vector clock for this sender
        with self._lock:
            current = self._vector_clocks.get(sender_core, VectorClock())
            updated_clock = current.tick(sender_core)
            self._vector_clocks[sender_core] = updated_clock

        envelope = CausalEnvelope(
            topic=topic,
            sender_core=sender_core,
            nexus_epoch=nexus_epoch,
            vector_clock=updated_clock,
            payload=payload,
            clearance_hash=clearance_token.token_hash if clearance_token else "",
            is_dissent=is_dissent or topic == Topic.DISSENT,
        )

        # Clearance gate — capability, not worth
        if not is_dissent and topic != Topic.DISSENT:
            if clearance_token is None or not clearance_token.can_broadcast:
                logger.warning(
                    f"[IPC] {sender_core} attempted broadcast on {topic} "
                    f"without ELEVATED clearance — logged, not delivered"
                )
                with self._lock:
                    self._message_log.append(envelope)
                return envelope  # logged, not delivered

        # Deliver to all subscribers
        with self._lock:
            handlers = list(self._subscribers.get(topic, []))
            self._message_log.append(envelope)

        for handler in handlers:
            try:
                handler(envelope)
            except Exception as e:
                logger.error(f"[IPC] Subscriber error on {topic}: {e}")

        logger.debug(
            f"[IPC] broadcast | {sender_core} → {topic} "
            f"epoch={nexus_epoch} clock={updated_clock.clocks} "
            f"subscribers={len(handlers)}"
        )
        return envelope

    def get_log(self) -> list[CausalEnvelope]:
        """Return full causal message log — for audit and replay."""
        with self._lock:
            return list(self._message_log)

    def get_vector_clock(self, core_id: str) -> VectorClock:
        with self._lock:
            return self._vector_clocks.get(core_id, VectorClock())


# Module-level singleton bus — shared by all cores in-process
_BUS: Optional[LocalBus] = None


def get_bus() -> LocalBus:
    """Get or create the module-level IPC bus singleton."""
    global _BUS
    if _BUS is None:
        _BUS = LocalBus()
    return _BUS


def reset_bus() -> None:
    """Reset the bus — for testing only."""
    global _BUS
    _BUS = None
