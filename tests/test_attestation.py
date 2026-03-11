"""Unit tests for gaia_core.attestation.tpm_quote."""
import pytest
from gaia_core.attestation.tpm_quote import TPMQuote, AttestationResult


def test_simulated_quote_returns_result():
    tpm = TPMQuote(node_id="test-node-001", use_simulation=True)
    result = tpm.generate_quote(nonce="abc123")
    assert isinstance(result, AttestationResult)
    assert result.verified is True
    assert result.method == "simulated"
    assert result.node_id == "test-node-001"
    assert result.nonce == "abc123"


def test_simulated_quote_default_pcrs():
    tpm = TPMQuote(node_id="test-node-001", use_simulation=True)
    result = tpm.generate_quote(nonce="xyz")
    assert set(result.pcr_values.keys()) == {0, 1, 2, 3, 4, 7}


def test_simulated_quote_custom_pcrs():
    tpm = TPMQuote(node_id="test-node-002", use_simulation=True)
    result = tpm.generate_quote(nonce="test", pcr_selection=[0, 7])
    assert set(result.pcr_values.keys()) == {0, 7}


def test_simulated_quote_deterministic():
    tpm = TPMQuote(node_id="deterministic-node", use_simulation=True)
    r1 = tpm.generate_quote(nonce="same-nonce")
    r2 = tpm.generate_quote(nonce="same-nonce")
    assert r1.quote_signature == r2.quote_signature
    assert r1.pcr_values == r2.pcr_values


def test_hardware_quote_raises_not_implemented():
    tpm = TPMQuote(node_id="test", use_simulation=False)
    with pytest.raises(NotImplementedError, match="ADR-003"):
        tpm._hardware_quote(nonce="x", pcr_selection=[0])
