"""VectorClockService for the GAIA IPC layer.

Builds on gaia_core.models.VectorClock (which already implements
increment, merge, and happened_before) and adds:
  - per-node clock management
  - stamp/unstamp helpers for GaiaEnvelope
  - concurrent-with detection

Do NOT duplicate the VectorClock dataclass — import and extend it.
"""
from __future__ import annotations

import logging
from threading import Lock

from gaia_core.models import VectorClock
from gaia_core.ipc.contracts import GaiaEnvelope

log = logging.getLogger(__name__)


class VectorClockService:
    """Per-node vector clock manager for IPC causal ordering."""

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self._clock = VectorClock()
        self._lock = Lock()

    def tick(self) -> VectorClock:
        """Increment local clock for a send event. Returns new clock."""
        with self._lock:
            self._clock = self._clock.increment(self.node_id)
            return self._clock

    def receive(self, remote_versions: dict[str, int]) -> VectorClock:
        """Merge remote clock on receive, then increment local. Returns new clock."""
        with self._lock:
            remote = VectorClock(versions=remote_versions)
            self._clock = self._clock.merge(remote).increment(self.node_id)
            return self._clock

    def current(self) -> VectorClock:
        with self._lock:
            return self._clock

    def stamp(self, envelope: GaiaEnvelope) -> GaiaEnvelope:
        """Attach current vector clock to an outgoing envelope (tick first)."""
        clock = self.tick()
        envelope.causal_clock = dict(clock.versions)
        return envelope

    def unstamp(self, envelope: GaiaEnvelope) -> VectorClock:
        """Extract and merge the clock from an incoming envelope."""
        return self.receive(envelope.causal_clock)

    def happened_before(self, a: dict[str, int], b: dict[str, int]) -> bool:
        """True if clock a causally precedes clock b."""
        return VectorClock(a).happened_before(VectorClock(b))

    def concurrent_with(self, a: dict[str, int], b: dict[str, int]) -> bool:
        """True if neither a happened-before b nor b happened-before a."""
        va, vb = VectorClock(a), VectorClock(b)
        return not va.happened_before(vb) and not vb.happened_before(va)
