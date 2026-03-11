"""
GAIA ADR-006 — Attestation Quote Generation and Remote Verification
Provides structured quote creation and verification against a known identity root.
"""
from __future__ import annotations
import hashlib
import logging
import os
import time
from dataclasses import dataclass
from typing import Optional
from .identity_root import IdentityRoot

log = logging.getLogger(__name__)


@dataclass
class AttestationQuote:
    """
    Structured attestation quote for remote verification.
    Contains nonce, timestamp, PCR list, raw quote blob, and identity root hex.
    """
    node_id: str
    nonce: bytes
    pcr_list: list[int]
    quote_blob: bytes
    identity_root_hex: str
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = time.time()

    @classmethod
    def generate(
        cls,
        identity: IdentityRoot,
        pcr_list: list[int] | None = None,
        nonce: bytes | None = None
    ) -> "AttestationQuote":
        """Generate a fresh attestation quote from an IdentityRoot."""
        if nonce is None:
            nonce = os.urandom(32)
        if pcr_list is None:
            pcr_list = [0, 1, 7]
        quote_blob = identity.generate_quote(nonce, pcr_list)
        log.info(f"[AttestationQuote] Quote generated for node {identity.node_id!r}")
        return cls(
            node_id=identity.node_id,
            nonce=nonce,
            pcr_list=pcr_list,
            quote_blob=quote_blob,
            identity_root_hex=identity.root_hex
        )

    def verify(self, expected_root_hex: str) -> bool:
        """
        Basic remote verification: confirm identity root matches expected.
        Full TPM quote verification requires tpm2-tools on verifier side.
        """
        match = self.identity_root_hex == expected_root_hex
        if match:
            log.info(f"[AttestationQuote] Verification PASSED for node {self.node_id!r}")
        else:
            log.warning(f"[AttestationQuote] Verification FAILED for node {self.node_id!r}")
        return match

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "nonce_hex": self.nonce.hex(),
            "pcr_list": self.pcr_list,
            "quote_blob_hex": self.quote_blob.hex(),
            "identity_root_hex": self.identity_root_hex,
            "timestamp": self.timestamp
        }
