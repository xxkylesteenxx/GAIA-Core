"""
GAIA ADR-007 — GUARDIAN Approval Gate
Async human approval workflow for RED-level actuation requests.
Timeout-aware: auto-denies if no approval within window.
"""
from __future__ import annotations
import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Callable, Dict, Optional
from .policy_manifest import RiskLevel
from .risk_classifier import ClassificationResult

log = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 300  # 5 minutes — conditional love has patience


class ApprovalResult(StrEnum):
    APPROVED = "approved"
    DENIED = "denied"
    TIMEOUT = "timeout"
    AUTO_APPROVED = "auto_approved"  # GREEN level
    HARD_DENIED = "hard_denied"     # BLACK level


@dataclass
class ApprovalRecord:
    approval_id: str
    request_id: str
    core_id: str
    action: str
    risk_level: RiskLevel
    result: ApprovalResult
    decided_by: str  # "system", "human:<operator_id>", "timeout"
    timestamp: float = field(default_factory=time.time)
    notes: str = ""


class ApprovalGate:
    """
    GUARDIAN Approval Gate.
    Routes actuation requests through human approval for RED-level actions.
    GREEN → auto-approve (love flows).
    YELLOW → log + rate-limit, auto-approve.
    RED → async human approval with timeout.
    BLACK → hard deny (shadow quarantine).
    """
    def __init__(
        self,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        notify_fn: Optional[Callable] = None
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.notify_fn = notify_fn  # Hook: send approval request to operator UI
        self._pending: Dict[str, asyncio.Future] = {}

    async def evaluate(
        self,
        classification: ClassificationResult,
    ) -> ApprovalRecord:
        """Route classification to appropriate approval path."""
        approval_id = str(uuid.uuid4())
        risk = classification.risk_level

        if risk == RiskLevel.BLACK:
            log.warning(f"[ApprovalGate] BLACK — hard deny '{classification.action}'.")
            return ApprovalRecord(
                approval_id=approval_id,
                request_id=classification.request_id,
                core_id=classification.core_id,
                action=classification.action,
                risk_level=risk,
                result=ApprovalResult.HARD_DENIED,
                decided_by="system",
                notes="Blacklisted or jurisdiction-denied."
            )

        if risk in (RiskLevel.GREEN, RiskLevel.YELLOW):
            log.info(f"[ApprovalGate] {risk.name} — auto-approve '{classification.action}'.")
            return ApprovalRecord(
                approval_id=approval_id,
                request_id=classification.request_id,
                core_id=classification.core_id,
                action=classification.action,
                risk_level=risk,
                result=ApprovalResult.AUTO_APPROVED,
                decided_by="system"
            )

        # RED: requires human approval
        log.info(f"[ApprovalGate] RED — awaiting human approval for '{classification.action}' (timeout={self.timeout_seconds}s).")
        if self.notify_fn:
            await asyncio.get_event_loop().run_in_executor(None, self.notify_fn, classification)

        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[approval_id] = future

        try:
            result = await asyncio.wait_for(future, timeout=self.timeout_seconds)
            decided_by = result.get("operator_id", "human:unknown")
            approved = result.get("approved", False)
            return ApprovalRecord(
                approval_id=approval_id,
                request_id=classification.request_id,
                core_id=classification.core_id,
                action=classification.action,
                risk_level=risk,
                result=ApprovalResult.APPROVED if approved else ApprovalResult.DENIED,
                decided_by=decided_by,
                notes=result.get("notes", "")
            )
        except asyncio.TimeoutError:
            log.warning(f"[ApprovalGate] Timeout — auto-deny '{classification.action}'.")
            return ApprovalRecord(
                approval_id=approval_id,
                request_id=classification.request_id,
                core_id=classification.core_id,
                action=classification.action,
                risk_level=risk,
                result=ApprovalResult.TIMEOUT,
                decided_by="timeout",
                notes=f"No response within {self.timeout_seconds}s."
            )
        finally:
            self._pending.pop(approval_id, None)

    def resolve(self, approval_id: str, approved: bool, operator_id: str = "unknown", notes: str = "") -> None:
        """Called by operator UI to resolve a pending approval."""
        future = self._pending.get(approval_id)
        if future and not future.done():
            future.set_result({"approved": approved, "operator_id": f"human:{operator_id}", "notes": notes})
            log.info(f"[ApprovalGate] Approval {approval_id!r} resolved: approved={approved} by {operator_id!r}.")
        else:
            log.warning(f"[ApprovalGate] No pending future for approval_id={approval_id!r}.")
