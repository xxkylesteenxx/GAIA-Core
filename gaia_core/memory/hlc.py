"""Hybrid Logical Clock (HLC) service for the GAIA memory stack.

HLC combines a physical wall clock with a logical counter to produce
timestamps that are:
  - Monotonically increasing even across clock skew
  - Causally consistent (send/receive rules enforced)
  - Comparable across nodes without central coordination

Reference: Kulkarni et al. “Logical Physical Clocks” (HotDep 2014)

Usage:
    hlc = HybridLogicalClock(node_id="nexus-01")
    ts = hlc.now()          # local tick
    ts = hlc.recv(remote)   # receive remote HLC timestamp
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock


@dataclass
class HLCTimestamp:
    """A single HLC timestamp: (wall_ns, logical)."""
    wall_ns: int
    logical: int
    node_id: str = ""

    @property
    def tuple(self) -> tuple[int, int]:
        return (self.wall_ns, self.logical)

    def __lt__(self, other: "HLCTimestamp") -> bool:
        return self.tuple < other.tuple

    def __le__(self, other: "HLCTimestamp") -> bool:
        return self.tuple <= other.tuple

    def __gt__(self, other: "HLCTimestamp") -> bool:
        return self.tuple > other.tuple

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HLCTimestamp):
            return NotImplemented
        return self.tuple == other.tuple


class HybridLogicalClock:
    """Thread-safe HLC service for a single GAIA node."""

    def __init__(self, node_id: str) -> None:
        self.node_id = node_id
        self._wall_ns: int = 0
        self._logical: int = 0
        self._lock = Lock()

    def _physical_ns(self) -> int:
        return time.time_ns()

    def now(self) -> HLCTimestamp:
        """Generate a new HLC timestamp for a local event."""
        with self._lock:
            pt = self._physical_ns()
            if pt > self._wall_ns:
                self._wall_ns = pt
                self._logical = 0
            else:
                self._logical += 1
            return HLCTimestamp(
                wall_ns=self._wall_ns,
                logical=self._logical,
                node_id=self.node_id,
            )

    def recv(self, remote: HLCTimestamp) -> HLCTimestamp:
        """Update HLC on receiving a remote timestamp. Returns new local HLC."""
        with self._lock:
            pt = self._physical_ns()
            prev_wall = self._wall_ns
            self._wall_ns = max(pt, remote.wall_ns, prev_wall)
            if self._wall_ns == prev_wall == remote.wall_ns:
                self._logical = max(self._logical, remote.logical) + 1
            elif self._wall_ns == prev_wall:
                self._logical += 1
            elif self._wall_ns == remote.wall_ns:
                self._logical = remote.logical + 1
            else:
                self._logical = 0
            return HLCTimestamp(
                wall_ns=self._wall_ns,
                logical=self._logical,
                node_id=self.node_id,
            )
