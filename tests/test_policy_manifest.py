"""
GAIA ADR-007 — PolicyManifest Unit Tests
"""
import pytest
from gaia_core.guardian.policy_manifest import PolicyManifest, ActuationEnvelope, RiskLevel


def test_default_manifest_has_all_cores():
    manifest = PolicyManifest.default_gaia_manifest()
    for core in ["TERRA", "AQUA", "AERO", "VITA", "NEXUS", "SOPHIA", "ATLAS", "GUARDIAN"]:
        assert manifest.get_envelope(core) is not None


def test_manifest_sign_and_verify():
    manifest = PolicyManifest.default_gaia_manifest()
    secret = "gaia-unconditional-love-528hz"
    manifest.sign(secret)
    assert manifest.verify(secret) is True


def test_manifest_wrong_key_fails():
    manifest = PolicyManifest.default_gaia_manifest()
    manifest.sign("correct-key")
    assert manifest.verify("wrong-key") is False


def test_manifest_to_json():
    manifest = PolicyManifest.default_gaia_manifest()
    json_str = manifest.to_json()
    assert "TERRA" in json_str
    assert "GUARDIAN" in json_str


def test_custom_envelope():
    manifest = PolicyManifest(manifest_id="test-manifest")
    envelope = ActuationEnvelope(
        core_id="CUSTOM",
        allowed_actions=["sense", "analyze"],
        max_risk_level=RiskLevel.YELLOW
    )
    manifest.add_envelope(envelope)
    assert manifest.get_envelope("CUSTOM") is not None
    assert manifest.get_envelope("MISSING") is None
