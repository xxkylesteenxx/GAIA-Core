"""Typed models for GAIA inter-core messages, health, and state.

Spec ref: PYTHON-ORCHESTRATION-SPEC §5
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HealthStatus(Enum):
    HEALTHY  = "healthy"
    DEGRADED = "degraded"
    FAILED   = "failed"
    STARTING = "starting"
    STOPPED  = "stopped"

    # Backward-compat alias
    OK = "healthy"


@dataclass
class HealthReport:
    """Rich health record returned by the registry health table."""
    core_name: str
    status:    HealthStatus
    timestamp: float = field(default_factory=time.time)


@dataclass
class CoreMessage:
    """Typed inter-core message (used by CoreMessageBus and registry.send).

    Spec ref: PYTHON-ORCHESTRATION-SPEC §5
    """
    sender:      str
    topic:       str
    payload:     dict[str, Any]
    recipient:   str | None = None
    trust_label: str        = "bounded"
    timestamp:   float      = field(default_factory=time.time)

    def is_broadcast(self) -> bool:
        return self.recipient is None


# Public alias
GaiaMessage = CoreMessage


@dataclass
class StateSnapshot:
    """Point-in-time state export from a single core."""
    core_name: str
    health:    HealthStatus
    state:     dict[str, Any]
    timestamp: float = field(default_factory=time.time)

    @property
    def values(self) -> dict[str, Any]:
        return self.state


@dataclass
class StateUpdate:
    """A planetary state update broadcast by the StatePropagator.

    Spec ref: PYTHON-ORCHESTRATION-SPEC §7
    """
    source:    str
    scope:     str
    values:    dict[str, Any]
    summary:   str   = ""
    timestamp: float = field(default_factory=time.time)
