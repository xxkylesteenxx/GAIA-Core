"""Typed models for GAIA inter-core messages, health, and state.

Spec ref: PYTHON-ORCHESTRATION-SPEC §5
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()


# ── Health ─────────────────────────────────────────────────────────────────────

class HealthStatus(str, Enum):
    """Core health states.

    Inherits from str so status values serialize directly as JSON strings
    without needing .value access.
    """
    STARTING = "starting"
    HEALTHY  = "healthy"
    DEGRADED = "degraded"
    STOPPED  = "stopped"
    FAILED   = "failed"


@dataclass(slots=True)
class HealthReport:
    """Returned by GaiaCore.health_check() and the registry health table."""
    core_id:    str
    status:     HealthStatus
    detail:     str = ""
    updated_at: str = field(default_factory=utc_now_iso)


# ── Messages ─────────────────────────────────────────────────────────────────

@dataclass(slots=True)
class GaiaMessage:
    """Typed inter-core message.

    Spec ref: PYTHON-ORCHESTRATION-SPEC §5

    trust_label values:
      'internal'  — same-process registry delivery (default)
      'bounded'   — standard cross-core message
      'critical'  — high-trust; GUARDIAN audits senders claiming this label
    """
    sender:      str
    recipient:   str | None
    topic:       str
    payload:     dict[str, Any]
    trust_label: str = "internal"
    timestamp:   str = field(default_factory=utc_now_iso)

    def is_broadcast(self) -> bool:
        return self.recipient is None


# Backward-compat alias
CoreMessage = GaiaMessage


# ── State ────────────────────────────────────────────────────────────────────

@dataclass(slots=True)
class CoreState:
    """Point-in-time state export from a single core.

    `summary` is a human-readable one-line description of current state.
    `values`  is the machine-readable key/value payload.
    """
    core_id:    str
    domain:     str
    summary:    str
    values:     dict[str, Any] = field(default_factory=dict)
    updated_at: str            = field(default_factory=utc_now_iso)


# Backward-compat alias
StateSnapshot = CoreState


@dataclass(slots=True)
class StateUpdate:
    """A directed or broadcast state update from the StatePropagator.

    `values` is typed as Mapping[str, Any] (read-only view) to prevent
    accidental mutation of the source dict by receiving cores.

    Spec ref: PYTHON-ORCHESTRATION-SPEC §7
    """
    source:     str
    scope:      str
    values:     Mapping[str, Any]
    summary:    str = ""
    updated_at: str = field(default_factory=utc_now_iso)
