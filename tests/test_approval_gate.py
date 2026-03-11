"""
GAIA ADR-007 — ApprovalGate Unit Tests
"""
import asyncio
import pytest
from gaia_core.guardian.policy_manifest import RiskLevel
from gaia_core.guardian.risk_classifier import ClassificationResult
from gaia_core.guardian.approval_gate import ApprovalGate, ApprovalResult


def make_classification(risk_level: RiskLevel, action: str = "test_action") -> ClassificationResult:
    return ClassificationResult(
        request_id="req-test",
        core_id="NEXUS",
        action=action,
        risk_level=risk_level,
        reason="test",
        allowed=risk_level < RiskLevel.BLACK
    )


@pytest.mark.asyncio
async def test_green_auto_approved():
    gate = ApprovalGate(timeout_seconds=5)
    record = await gate.evaluate(make_classification(RiskLevel.GREEN))
    assert record.result == ApprovalResult.AUTO_APPROVED


@pytest.mark.asyncio
async def test_yellow_auto_approved():
    gate = ApprovalGate(timeout_seconds=5)
    record = await gate.evaluate(make_classification(RiskLevel.YELLOW))
    assert record.result == ApprovalResult.AUTO_APPROVED


@pytest.mark.asyncio
async def test_black_hard_denied():
    gate = ApprovalGate(timeout_seconds=5)
    record = await gate.evaluate(make_classification(RiskLevel.BLACK))
    assert record.result == ApprovalResult.HARD_DENIED


@pytest.mark.asyncio
async def test_red_timeout():
    gate = ApprovalGate(timeout_seconds=1)  # 1 second timeout for test
    record = await gate.evaluate(make_classification(RiskLevel.RED))
    assert record.result == ApprovalResult.TIMEOUT


@pytest.mark.asyncio
async def test_red_human_approval():
    gate = ApprovalGate(timeout_seconds=5)
    classification = make_classification(RiskLevel.RED, action="shutdown_core")

    async def approve_after_delay():
        await asyncio.sleep(0.1)
        pending_id = list(gate._pending.keys())[0]
        gate.resolve(pending_id, approved=True, operator_id="kyle", notes="Approved by human")

    result_task = asyncio.create_task(gate.evaluate(classification))
    await asyncio.create_task(approve_after_delay())
    record = await result_task
    assert record.result == ApprovalResult.APPROVED
    assert "kyle" in record.decided_by
