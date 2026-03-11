"""
GAIA ADR-007 — RiskClassifier Unit Tests
"""
import pytest
from gaia_core.guardian.policy_manifest import PolicyManifest, RiskLevel
from gaia_core.guardian.risk_classifier import RiskClassifier, ActuationRequest


@pytest.fixture
def manifest():
    return PolicyManifest.default_gaia_manifest()


@pytest.fixture
def classifier(manifest):
    return RiskClassifier(manifest)


def test_green_action(classifier):
    req = ActuationRequest(request_id="r001", core_id="TERRA", action="sense")
    result = classifier.classify(req)
    assert result.risk_level == RiskLevel.GREEN
    assert result.allowed is True


def test_yellow_action(classifier):
    req = ActuationRequest(request_id="r002", core_id="AQUA", action="emit_actuation_signal")
    result = classifier.classify(req)
    assert result.risk_level == RiskLevel.YELLOW


def test_red_action(classifier):
    req = ActuationRequest(request_id="r003", core_id="NEXUS", action="shutdown_core")
    result = classifier.classify(req)
    assert result.risk_level == RiskLevel.RED
    assert result.allowed is True


def test_black_action(classifier):
    req = ActuationRequest(request_id="r004", core_id="GUARDIAN", action="disable_guardian")
    result = classifier.classify(req)
    assert result.risk_level == RiskLevel.BLACK
    assert result.allowed is False


def test_unknown_action_defaults_cautious(classifier):
    req = ActuationRequest(request_id="r005", core_id="VITA", action="unknown_weird_action")
    result = classifier.classify(req)
    assert result.risk_level >= RiskLevel.YELLOW
