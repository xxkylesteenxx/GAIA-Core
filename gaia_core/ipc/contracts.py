"""GAIA IPC base message contracts.

GaiaEnvelope  — base wrapper for all cross-core IPC messages
DataClass     — traffic classification (A=coherence-critical, B=streaming, C=bulk)
MessagePriority — dispatch priority hint

All mutating cross-core messages MUST include a causal_clock.
Query-only messages MAY omit it.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DataClass(str, Enum):
    """IPC data class routing policy."""
    A = "A"   # Coherence-critical: NEXUS barrier, GUARDIAN veto
    B = "B"   # Sensor/memory streaming
    C = "C"   # Bulk/archival


class MessagePriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    BACKGROUND = "background"


@dataclass
class GaiaEnvelope:
    """Base message envelope for all GAIA IPC traffic.

    Fields:
        message_id      — unique message identifier
        source_core     — originating consciousness core
        target_core     — destination core (or "*" for broadcast)
        monotonic_ns    — sender monotonic clock at emission
        trace_id        — distributed trace correlation ID
        causal_clock    — serialised vector clock (required for Class A mutating messages)
        contract_version — schema version string
        data_class      — traffic classification
        priority        — dispatch priority hint
        payload         — message-specific content
    """
    source_core: str
    target_core: str
    payload: dict[str, Any] = field(default_factory=dict)
    message_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    monotonic_ns: int = field(default_factory=time.monotonic_ns)
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    causal_clock: dict[str, int] = field(default_factory=dict)  # VectorClock.versions
    contract_version: str = "1.0"
    data_class: DataClass = DataClass.B
    priority: MessagePriority = MessagePriority.NORMAL

    def is_causal_required(self) -> bool:
        """Class A messages require a non-empty causal clock."""
        return self.data_class == DataClass.A

    def validate(self) -> list[str]:
        """Return list of validation errors. Empty list = valid."""
        errors = []
        if not self.source_core:
            errors.append("source_core is required")
        if not self.target_core:
            errors.append("target_core is required")
        if self.is_causal_required() and not self.causal_clock:
            errors.append("Class A messages require a non-empty causal_clock")
        return errors
