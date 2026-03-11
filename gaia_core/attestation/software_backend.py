"""
GAIA ADR-006 — Software Identity Backend (ECDSA P-256 fallback)
Used when TPM 2.0 hardware is not available (IoT/edge/dev environments).
"""
from __future__ import annotations
import hashlib
import logging
import os
from dataclasses import dataclass, field
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend

log = logging.getLogger(__name__)


@dataclass
class SoftwareBackend:
    """
    Software-backed identity root using ECDSA P-256.
    Key material stored in-process (not hardware-protected).
    Suitable for dev, CI, and TPM-less IoT/edge nodes.
    """
    _private_key: ec.EllipticCurvePrivateKey = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        self._private_key = ec.generate_private_key(
            ec.SECP256R1(), default_backend()
        )
        log.info("[SoftwareBackend] ECDSA P-256 identity key generated.")

    @property
    def available(self) -> bool:
        return True  # Always available

    # ------------------------------------------------------------------
    # Identity root derivation
    # ------------------------------------------------------------------
    def derive_identity_root(self, node_id: str) -> bytes:
        """
        Derive 256-bit identity root from P-256 public key + node_id.
        Returns raw 32 bytes.
        """
        pub_bytes = self._private_key.public_key().public_bytes(
            serialization.Encoding.X962,
            serialization.PublicFormat.UncompressedPoint
        )
        digest = hashlib.sha256(pub_bytes + node_id.encode()).digest()
        log.info("[SoftwareBackend] Software identity root derived.")
        return digest

    # ------------------------------------------------------------------
    # Signing / attestation
    # ------------------------------------------------------------------
    def sign(self, data: bytes) -> bytes:
        """ECDSA P-256 signature over data."""
        return self._private_key.sign(data, ec.ECDSA(hashes.SHA256()))

    def generate_quote(self, nonce: bytes, pcr_list: list[int]) -> bytes:
        """
        Software-simulated attestation quote.
        PCR values are SHA-256 hashes of the nonce + pcr index.
        """
        pcr_values = b"".join(
            hashlib.sha256(nonce + p.to_bytes(1, "big")).digest()
            for p in pcr_list
        )
        payload = nonce + pcr_values
        signature = self.sign(payload)
        return payload + signature
