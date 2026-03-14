"""Typed models for GAIA inter-core messages, health, and state.

Spec ref: PYTHON-ORCHESTRATION-SPEC §5
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ── Health ─────────────────────────────────────────────────────────────────────

class HealthStatus(Enum):
    OK       = "ok"
    DEGRADED = "degraded"
    FAILED   = "failed"
    STARTING = "starting"
    STOPPED  = "stopped"


@dataclass
class HealthReport:
    """Rich health record returned by the registry health table."""
    core_name: str
    status:    HealthStatus
    timestamp: float = field(default_factory=time.time)


# ── Messages ─────────────────────────────────────────────────────────────────

@dataclass
class CoreMessage:
    """Internal typed inter-core message (used by CoreMessageBus).

    Spec ref: PYTHON-ORCHESTRATION-SPEC §5
    """
    sender:      str
    topic:       str
    payload:     dict[str, Any]
    recipient:   str | None = None       # None = broadcast
    trust_label: str        = "bounded"  # "bounded" | "critical" | "monitor"
    timestamp:   float      = field(default_factory=time.time)

    def is_broadcast(self) -> bool:
        return self.recipient is None


# GaiaMessage is the public-facing alias with an explicit payload field
# for use in demo scripts and external integrations.
GaiaMessage = CoreMessage


# ── State ────────────────────────────────────────────────────────────────────

@dataclass
class StateSnapshot:
    """Point-in-time state export from a single core."""
    core_name: str
    health:    HealthStatus
    state:     dict[str, Any]
    timestamp: float = field(default_factory=time.time)

    # Convenience alias so callers can use .values as well as .state
    @property
    def values(self) -> dict[str, Any]:
        return self.state


@dataclass
class StateUpdate:
    """A planetary state update broadcast by the StatePropagator.

    Spec ref: PYTHON-ORCHESTRATION-SPEC §7
    """
    source:  str
    scope:   str                    # e.g. "global", "regional", domain tag
    values:  dict[str, Any]
    summary: str = ""
    timestamp: float = field(default_factory=time.time)
