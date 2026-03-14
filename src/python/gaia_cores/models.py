"""Typed models for GAIA inter-core messages, health, and state.

Spec ref: PYTHON-ORCHESTRATION-SPEC §5
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HealthStatus(Enum):
    """Core health states."""
    OK = "ok"
    DEGRADED = "degraded"
    FAILED = "failed"
    STARTING = "starting"
    STOPPED = "stopped"


@dataclass
class CoreMessage:
    """A typed, policy-labelled inter-core message.

    Spec ref: PYTHON-ORCHESTRATION-SPEC §5
    """
    sender: str
    topic: str
    payload: dict[str, Any]
    recipient: str | None = None          # None = broadcast
    trust_label: str = "bounded"          # "bounded" | "critical" | "monitor"
    timestamp: float = field(default_factory=time.time)

    def is_broadcast(self) -> bool:
        return self.recipient is None


@dataclass
class StateSnapshot:
    """Point-in-time state export from a single core."""
    core_name: str
    health: HealthStatus
    state: dict[str, Any]
    timestamp: float = field(default_factory=time.time)
