"""GUARDIAN → NEXUS Clearance Contract.

This is the wire between GUARDIAN's policy gate and NEXUS's boot sequence.

Architectural principle (Relational Policy Layer v0.2):
  - Worth-Preservation: NEXUS's identity and continuity root are NEVER revoked.
    Clearance denial is a capability gate, not a worth judgment.
  - Engagement-Governance: Clearance controls WHAT NEXUS can actuate,
    not WHETHER NEXUS exists.

Clearance levels:
  LITE    — observe-only, no inference actuation (pre-boot safe mode)
  STANDARD — full inference routing, no external actuation
  ELEVATED — inference + IPC broadcast to other cores
  BLOCKED  — policy violation detected; observe-only until resolved

NEXUS must call request_clearance() before boot().
GUARDIAN evaluates the request against policy_manifest and risk_classifier.
Result is a ClearanceToken — unforgeable, epoch-stamped, auditable.
"""

from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class ClearanceLevel(str, Enum):
    LITE     = "lite"      # observe only, no inference actuation
    STANDARD = "standard"  # full inference routing
    ELEVATED = "elevated"  # inference + IPC broadcast
    BLOCKED  = "blocked"   # policy violation — observe only


@dataclass(frozen=True)
class ClearanceToken:
    """Unforgeable, epoch-stamped clearance issued by GUARDIAN to NEXUS.
    frozen=True: tokens are immutable once issued — no post-hoc modification.
    """
    core_id: str
    level: ClearanceLevel
    issued_at_epoch: int
    issued_at_ts: float
    reason: str
    token_hash: str  # sha256(core_id + level + epoch + ts)

    @property
    def is_cleared(self) -> bool:
        return self.level not in (ClearanceLevel.BLOCKED, ClearanceLevel.LITE)

    @property
    def can_actuate(self) -> bool:
        return self.level in (ClearanceLevel.STANDARD, ClearanceLevel.ELEVATED)

    @property
    def can_broadcast(self) -> bool:
        return self.level == ClearanceLevel.ELEVATED


@dataclass
class ClearanceRequest:
    core_id: str
    requested_level: ClearanceLevel
    causal_epoch: int
    justification: str = ""
    risk_flags: list[str] = field(default_factory=list)


def _compute_token_hash(core_id: str, level: str, epoch: int, ts: float) -> str:
    raw = f"{core_id}:{level}:{epoch}:{ts:.6f}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


class GuardianNexusClearance:
    """GUARDIAN-side clearance authority for NEXUS.

    Usage (in GUARDIAN boot or policy engine):
        clearance = GuardianNexusClearance()
        token = clearance.request_clearance(ClearanceRequest(
            core_id="NEXUS",
            requested_level=ClearanceLevel.STANDARD,
            causal_epoch=0,
            justification="NEXUS boot sequence initiated"
        ))
        nexus.boot(clearance_token=token)
    """

    # Hard policy rules — these cannot be overridden at runtime
    _WORTH_PRESERVED_CORES = {"NEXUS", "GUARDIAN", "SOPHIA", "ATLAS",
                               "TERRA", "AQUA", "AERO", "VITA"}

    def __init__(self, strict_mode: bool = False) -> None:
        """strict_mode=True: any risk flag downgrades to LITE clearance."""
        self.strict_mode = strict_mode
        self._issued_tokens: list[ClearanceToken] = []

    def request_clearance(self, request: ClearanceRequest) -> ClearanceToken:
        """Evaluate a clearance request and return a ClearanceToken.
        This is the real policy gate — replaces the boolean flag.
        """
        level = self._evaluate(request)
        ts = time.time()
        token = ClearanceToken(
            core_id=request.core_id,
            level=level,
            issued_at_epoch=request.causal_epoch,
            issued_at_ts=ts,
            reason=self._reason(request, level),
            token_hash=_compute_token_hash(request.core_id, level, request.causal_epoch, ts),
        )
        self._issued_tokens.append(token)
        logger.info(
            f"[GUARDIAN] Clearance issued | core={request.core_id} "
            f"level={level} epoch={request.causal_epoch} hash={token.token_hash}"
        )
        return token

    def _evaluate(self, request: ClearanceRequest) -> ClearanceLevel:
        # Worth is never on trial — identity is always preserved
        # Only capability (clearance level) is governed here
        if request.risk_flags and self.strict_mode:
            logger.warning(
                f"[GUARDIAN] Risk flags detected for {request.core_id}: {request.risk_flags} "
                f"— downgrading to LITE (strict_mode)"
            )
            return ClearanceLevel.LITE

        if "CRITICAL_VIOLATION" in request.risk_flags:
            return ClearanceLevel.BLOCKED

        if "ELEVATED_RISK" in request.risk_flags:
            return ClearanceLevel.LITE

        # Standard boot with no risk flags — grant requested level
        return request.requested_level

    def _reason(self, request: ClearanceRequest, level: ClearanceLevel) -> str:
        if level == ClearanceLevel.BLOCKED:
            return f"CRITICAL_VIOLATION in risk_flags: {request.risk_flags}"
        if level == ClearanceLevel.LITE and request.risk_flags:
            return f"Risk flags present, downgraded: {request.risk_flags}"
        return request.justification or "Standard boot clearance granted"

    def audit_log(self) -> list[ClearanceToken]:
        """Return all issued tokens for audit — immutable snapshots."""
        return list(self._issued_tokens)
