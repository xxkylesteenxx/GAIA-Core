from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(slots=True)
class GuardianDecision:
    allowed: bool
    reasons: List[str] = field(default_factory=list)


def evaluate_action(action: Dict[str, Any]) -> GuardianDecision:
    reasons: list[str] = []
    risk = action.get("risk_level", "medium")
    autonomous = bool(action.get("autonomous", False))
    jurisdiction_ok = bool(action.get("jurisdiction_ok", False))
    human_approved = bool(action.get("human_approved", False))

    if autonomous:
        reasons.append("autonomous actuation blocked")
    if not jurisdiction_ok:
        reasons.append("jurisdiction / legal basis not established")
    if not human_approved:
        reasons.append("meaningful human approval missing")
    if risk in {"high", "critical"}:
        reasons.append("high-risk action requires escalation path")

    return GuardianDecision(allowed=len(reasons) == 0, reasons=reasons)
