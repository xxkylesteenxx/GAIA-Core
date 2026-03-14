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
    HEALTHY  = "healthy"
    DEGRADED = "degraded"
    FAILED   = "failed"
    STARTING = "starting"
    STOPPED  = "stopped"


@dataclass
class HealthReport:
    """Rich health record returned by health_check() and the registry."""
    core_id:   str
    status:    HealthStatus
    domain:    str           = ""
    detail:    str           = ""
    timestamp: float         = field(default_factory=time.time)


# ── Messages ─────────────────────────────────────────────────────────────────

@dataclass
class GaiaMessage:
    """Typed inter-core message.

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


# Backward-compat alias
CoreMessage = GaiaMessage


# ── State ────────────────────────────────────────────────────────────────────

@dataclass
class CoreState:
    """Point-in-time state export from a single core."""
    core_id:   str
    domain:    str
    health:    HealthStatus
    values:    dict[str, Any]
    timestamp: float = field(default_factory=time.time)


# Backward-compat alias used by registry snapshot_all()
StateSnapshot = CoreState


@dataclass
class StateUpdate:
    """A directed or broadcast state update from a propagator.

    Spec ref: PYTHON-ORCHESTRATION-SPEC §7
    """
    source:    str
    scope:     str
    values:    dict[str, Any]
    summary:   str   = ""
    timestamp: float = field(default_factory=time.time)
