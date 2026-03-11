"""GuardianPolicyService — gRPC cross-core policy enforcement stub.

Handles:
  - PolicyCheck: evaluate an actuation request against current policy
  - VetoSignal: broadcast a hard veto to all registered listeners
  - RiskLevelUpdate: propagate updated risk level to all cores

This is a stub defining the interface. Real gRPC wiring requires
generated Protobuf clients (see gaia_core/ipc/proto/guardian/).

The stub is fully functional in-process for local and test operation.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable

from gaia_core.ipc.contracts import GaiaEnvelope, DataClass, MessagePriority

log = logging.getLogger(__name__)


class RiskLevel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    BLACK = "black"


@dataclass
class PolicyCheckRequest:
    requesting_core: str
    action_type: str
    action_payload: dict
    trace_id: str = ""


@dataclass
class PolicyCheckResponse:
    allowed: bool
    risk_level: RiskLevel
    reason: str = ""
    requires_human_approval: bool = False
    latency_ms: float = 0.0


@dataclass
class VetoSignal:
    source_core: str
    action_type: str
    reason: str
    timestamp_ns: int = field(default_factory=time.monotonic_ns)
    risk_level: RiskLevel = RiskLevel.RED


class GuardianPolicyService:
    """In-process GuardianPolicyService stub.

    Replace with gRPC-generated client for cross-host operation.
    """

    def __init__(self) -> None:
        self._risk_level = RiskLevel.GREEN
        self._veto_handlers: list[Callable[[VetoSignal], None]] = []
        self._risk_handlers: list[Callable[[RiskLevel], None]] = []

    def check(self, req: PolicyCheckRequest) -> PolicyCheckResponse:
        """Evaluate an actuation request against current risk level."""
        t0 = time.monotonic()
        risk = self._risk_level

        if risk == RiskLevel.BLACK:
            result = PolicyCheckResponse(
                allowed=False, risk_level=risk,
                reason="Hard deny: risk level BLACK",
                latency_ms=(time.monotonic() - t0) * 1000,
            )
        elif risk == RiskLevel.RED:
            result = PolicyCheckResponse(
                allowed=False, risk_level=risk,
                reason="Human approval required: risk level RED",
                requires_human_approval=True,
                latency_ms=(time.monotonic() - t0) * 1000,
            )
        elif risk == RiskLevel.YELLOW:
            result = PolicyCheckResponse(
                allowed=True, risk_level=risk,
                reason="Allowed with elevated logging: risk level YELLOW",
                latency_ms=(time.monotonic() - t0) * 1000,
            )
        else:
            result = PolicyCheckResponse(
                allowed=True, risk_level=risk,
                reason="Allowed: risk level GREEN",
                latency_ms=(time.monotonic() - t0) * 1000,
            )

        log.info(
            "PolicyCheck: core=%s action=%s allowed=%s risk=%s",
            req.requesting_core, req.action_type, result.allowed, risk.value,
        )
        return result

    def veto(self, signal: VetoSignal) -> None:
        """Broadcast a hard veto to all registered listeners."""
        log.warning(
            "GUARDIAN VETO: core=%s action=%s reason=%s",
            signal.source_core, signal.action_type, signal.reason,
        )
        for handler in self._veto_handlers:
            handler(signal)

    def set_risk_level(self, level: RiskLevel) -> None:
        """Update risk level and notify all registered handlers."""
        prev = self._risk_level
        self._risk_level = level
        log.info("GUARDIAN risk level: %s -> %s", prev.value, level.value)
        for handler in self._risk_handlers:
            handler(level)

    def on_veto(self, handler: Callable[[VetoSignal], None]) -> None:
        self._veto_handlers.append(handler)

    def on_risk_change(self, handler: Callable[[RiskLevel], None]) -> None:
        self._risk_handlers.append(handler)

    def to_envelope(self, payload: dict, data_class: DataClass = DataClass.A) -> GaiaEnvelope:
        """Wrap a GUARDIAN payload in a GaiaEnvelope."""
        return GaiaEnvelope(
            source_core="GUARDIAN",
            target_core="*",
            payload=payload,
            data_class=data_class,
            priority=MessagePriority.CRITICAL,
        )
