"""
GAIA ADR-006 — IdentityRoot Unit Tests (software backend)
"""
import pytest
from gaia_core.attestation.identity_root import IdentityRoot
from gaia_core.attestation.software_backend import SoftwareBackend
from gaia_core.attestation.pcr_policy import PCRPolicy


def test_identity_root_software_backend():
    identity = IdentityRoot(node_id="test-node-001", force_software=True)
    assert identity.backend_type == "software"
    assert len(identity.root_bytes) == 32
    assert len(identity.root_hex) == 64


def test_identity_root_determinism():
    """Same node_id should produce same root (per key)."""
    identity = IdentityRoot(node_id="gaia-node-alpha", force_software=True)
    root1 = identity.root_hex
    root2 = identity.root_hex
    assert root1 == root2


def test_identity_root_unique_per_node():
    id1 = IdentityRoot(node_id="node-A", force_software=True)
    id2 = IdentityRoot(node_id="node-B", force_software=True)
    assert id1.root_hex != id2.root_hex


def test_software_backend_sign():
    backend = SoftwareBackend()
    sig = backend.sign(b"hello gaia")
    assert isinstance(sig, bytes)
    assert len(sig) > 0


def test_pcr_policy_seal_unseal():
    import os
    policy = PCRPolicy(pcr_indices=[0, 1, 7])
    nonce = os.urandom(16)
    identity_root = os.urandom(32)
    pcr_values = policy.simulate_pcr_values(nonce)
    sealed = policy.seal(identity_root, pcr_values)
    assert isinstance(sealed, bytes)
    assert policy.unseal(identity_root, pcr_values) is True


def test_pcr_policy_tamper_detection():
    import os
    policy = PCRPolicy(pcr_indices=[0, 1, 7])
    nonce = os.urandom(16)
    identity_root = os.urandom(32)
    pcr_values = policy.simulate_pcr_values(nonce)
    policy.seal(identity_root, pcr_values)
    # Tamper: change PCR 0
    tampered = dict(pcr_values)
    tampered[0] = os.urandom(32)
    assert policy.unseal(identity_root, tampered) is False
