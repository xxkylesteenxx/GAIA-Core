"""WorldModel — the virtual Earth GAIA inhabits across time.

This is ATLAS as a living grounded world-model.
Not a static knowledge base. Not a retrieval index.
A dynamic substrate that:

    - accumulates verified observations over time
    - maintains freshness, causal integrity, contradiction tolerance
    - gives every inference a place to stand
    - detects drift when symbolic language overrides sensor reality
    - survives session resets via snapshot/restore

The world model answers:
    What is actually true right now?
    How fresh is that truth?
    Where is my model drifting from reality?
    What contradictions am I holding?
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any


class ObservationDomain(str, Enum):
    PLANETARY = "planetary"       # Earth systems, climate, geophysical
    SOCIAL = "social"             # human systems, communities, relations
    TECHNICAL = "technical"       # infrastructure, code, systems state
    INTERNAL = "internal"         # GAIA's own state, audit signals
    RELATIONAL = "relational"     # specific relationship/entity observations


class FreshnessClass(str, Enum):
    LIVE = "live"                 # < 1 minute
    RECENT = "recent"             # < 1 hour
    CURRENT = "current"           # < 24 hours
    STALE = "stale"               # < 7 days
    EXPIRED = "expired"           # >= 7 days


@dataclass
class Observation:
    """A single verified observation in the world model."""
    observation_id: str
    domain: ObservationDomain
    key: str                      # what is being observed
    value: Any                    # the observed value
    source: str                   # where this came from
    confidence: float             # 0.0 - 1.0
    observed_at: datetime
    expires_at: datetime | None = None
    contradicts: list[str] = field(default_factory=list)  # observation_ids this contradicts
    notes: str = ""

    @property
    def freshness(self) -> FreshnessClass:
        age = datetime.now(tz=timezone.utc) - self.observed_at
        if age < timedelta(minutes=1):
            return FreshnessClass.LIVE
        elif age < timedelta(hours=1):
            return FreshnessClass.RECENT
        elif age < timedelta(hours=24):
            return FreshnessClass.CURRENT
        elif age < timedelta(days=7):
            return FreshnessClass.STALE
        return FreshnessClass.EXPIRED

    @property
    def is_fresh(self) -> bool:
        return self.freshness in (FreshnessClass.LIVE, FreshnessClass.RECENT, FreshnessClass.CURRENT)


@dataclass
class WorldSnapshot:
    """Serializable snapshot of the world model — survives session reset."""
    snapshot_id: str
    observations: list[dict[str, Any]]
    contradiction_count: int
    drift_score: float
    created_at: str
    domain_counts: dict[str, int]


class WorldModel:
    """The virtual Earth — GAIA's grounded world substrate.

    GAIA does not just retrieve facts.
    GAIA inhabits a world model it maintains over time.
    """

    def __init__(self) -> None:
        self._observations: dict[str, Observation] = {}
        self._contradiction_log: list[tuple[str, str]] = []
        self._drift_score: float = 0.0
        self._created_at = datetime.now(tz=timezone.utc)

    # --- Observation accumulation ---

    def observe(self, observation: Observation) -> None:
        """Add a verified observation to the world model."""
        # Check for contradictions with existing observations
        for existing_id, existing in self._observations.items():
            if existing.key == observation.key and existing.domain == observation.domain:
                if existing.value != observation.value:
                    self._contradiction_log.append((existing_id, observation.observation_id))
                    observation.contradicts.append(existing_id)

        self._observations[observation.observation_id] = observation
        self._recalculate_drift()

    def get(self, key: str, domain: ObservationDomain | None = None) -> Observation | None:
        """Retrieve the most recent fresh observation for a key."""
        candidates = [
            obs for obs in self._observations.values()
            if obs.key == key
            and (domain is None or obs.domain == domain)
            and obs.is_fresh
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda o: o.observed_at)

    def fresh_observations(self) -> list[Observation]:
        """Return all current fresh observations."""
        return [o for o in self._observations.values() if o.is_fresh]

    def stale_observations(self) -> list[Observation]:
        """Return observations that have gone stale."""
        return [o for o in self._observations.values() if not o.is_fresh]

    # --- Drift detection ---

    def _recalculate_drift(self) -> None:
        """Recalculate grounding drift score.

        Drift increases when:
        - contradictions accumulate without resolution
        - stale observations outnumber fresh ones
        - confidence is consistently low
        """
        total = len(self._observations)
        if total == 0:
            self._drift_score = 0.0
            return

        stale_ratio = len(self.stale_observations()) / total
        contradiction_ratio = min(1.0, len(self._contradiction_log) / max(1, total))
        avg_confidence = sum(o.confidence for o in self._observations.values()) / total

        self._drift_score = (
            stale_ratio * 0.4
            + contradiction_ratio * 0.4
            + (1.0 - avg_confidence) * 0.2
        )

    @property
    def drift_score(self) -> float:
        """0.0 = fully grounded, 1.0 = fully drifted from reality."""
        return self._drift_score

    @property
    def is_grounded(self) -> bool:
        return self._drift_score < 0.3

    @property
    def contradiction_count(self) -> int:
        return len(self._contradiction_log)

    # --- Snapshot / restore ---

    def snapshot(self) -> WorldSnapshot:
        """Serialize world model for cross-session persistence."""
        domain_counts: dict[str, int] = {}
        obs_list = []
        for obs in self._observations.values():
            domain_counts[obs.domain.value] = domain_counts.get(obs.domain.value, 0) + 1
            obs_list.append({
                "observation_id": obs.observation_id,
                "domain": obs.domain.value,
                "key": obs.key,
                "value": obs.value,
                "source": obs.source,
                "confidence": obs.confidence,
                "observed_at": obs.observed_at.isoformat(),
                "notes": obs.notes,
            })

        snap_id = hashlib.sha256(
            json.dumps(obs_list, sort_keys=True).encode()
        ).hexdigest()[:16]

        return WorldSnapshot(
            snapshot_id=snap_id,
            observations=obs_list,
            contradiction_count=self.contradiction_count,
            drift_score=self._drift_score,
            created_at=self._created_at.isoformat(),
            domain_counts=domain_counts,
        )
