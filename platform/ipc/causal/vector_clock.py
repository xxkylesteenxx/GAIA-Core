"""Vector clock primitives for GAIA causal broadcast and cross-core synchronization."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Mapping


@dataclass(slots=True)
class VectorClock:
    """Small, dependency-free vector clock.

    The implementation is intentionally simple so it can be embedded in higher level
    IPC or replicated state layers without importing a large runtime.
    """

    counters: Dict[str, int] = field(default_factory=dict)

    def copy(self) -> "VectorClock":
        return VectorClock(dict(self.counters))

    def tick(self, actor: str) -> int:
        self.counters[actor] = self.counters.get(actor, 0) + 1
        return self.counters[actor]

    def update(self, actor: str, value: int) -> None:
        current = self.counters.get(actor, 0)
        if value > current:
            self.counters[actor] = value

    def merge(self, other: Mapping[str, int] | "VectorClock") -> "VectorClock":
        data = other.counters if isinstance(other, VectorClock) else other
        merged = self.copy()
        for actor, counter in data.items():
            merged.update(actor, int(counter))
        return merged

    def dominates(self, other: Mapping[str, int] | "VectorClock") -> bool:
        data = other.counters if isinstance(other, VectorClock) else other
        return all(self.counters.get(actor, 0) >= int(counter) for actor, counter in data.items())

    def happens_before(self, other: Mapping[str, int] | "VectorClock") -> bool:
        data = other.counters if isinstance(other, VectorClock) else other
        actors = set(self.counters) | set(data)
        leq = all(self.counters.get(a, 0) <= int(data.get(a, 0)) for a in actors)
        strict = any(self.counters.get(a, 0) < int(data.get(a, 0)) for a in actors)
        return leq and strict

    def concurrent_with(self, other: Mapping[str, int] | "VectorClock") -> bool:
        data = other.counters if isinstance(other, VectorClock) else other
        return not self.happens_before(data) and not VectorClock(dict(data)).happens_before(self)

    def to_dict(self) -> Dict[str, int]:
        return dict(self.counters)

    @classmethod
    def from_mapping(cls, value: Mapping[str, int] | None) -> "VectorClock":
        return cls({k: int(v) for k, v in (value or {}).items()})
