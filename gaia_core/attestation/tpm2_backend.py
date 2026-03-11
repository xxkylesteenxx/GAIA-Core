"""
GAIA ADR-006 — TPM 2.0 Identity Backend
Binds GAIA node identity to TPM 2.0 hardware endorsement keys.
Falls back gracefully to software backend if TPM unavailable.
"""
from __future__ import annotations
import hashlib
import logging
import subprocess
from dataclasses import dataclass, field
from typing import Optional

log = logging.getLogger(__name__)


@dataclass
class TPM2Backend:
    """
    Production TPM 2.0 backend using tpm2-tools subprocess interface.
    Primary binding: EK (Endorsement Key) + AK (Attestation Key).
    """
    tcti: str = "device:/dev/tpm0"
    _available: bool = field(default=False, init=False, repr=False)

    def __post_init__(self) -> None:
        self._available = self._probe_tpm()

    # ------------------------------------------------------------------
    # Availability
    # ------------------------------------------------------------------
    def _probe_tpm(self) -> bool:
        try:
            result = subprocess.run(
                ["tpm2_getcap", "properties-fixed"],
                capture_output=True, timeout=5
            )
            available = result.returncode == 0
            if available:
                log.info("[TPM2Backend] TPM 2.0 device detected.")
            else:
                log.warning("[TPM2Backend] TPM probe returned non-zero; falling back.")
            return available
        except (FileNotFoundError, subprocess.TimeoutExpired):
            log.warning("[TPM2Backend] tpm2-tools not found or timed out; TPM unavailable.")
            return False

    @property
    def available(self) -> bool:
        return self._available

    # ------------------------------------------------------------------
    # Identity root derivation
    # ------------------------------------------------------------------
    def derive_identity_root(self, node_id: str) -> bytes:
        """
        Derive 256-bit identity root by hashing EK public key + node_id.
        Returns raw 32 bytes.
        """
        if not self._available:
            raise RuntimeError("TPM 2.0 not available on this host.")
        ek_pub = self._read_ek_public()
        digest = hashlib.sha256(ek_pub + node_id.encode()).digest()
        log.info("[TPM2Backend] Identity root derived from EK public key.")
        return digest

    def _read_ek_public(self) -> bytes:
        result = subprocess.run(
            ["tpm2_createek", "--ek-context", "/tmp/ek.ctx", "--key-algorithm", "rsa",
             "--public", "/tmp/ek.pub"],
            capture_output=True, timeout=10
        )
        if result.returncode != 0:
            raise RuntimeError(f"tpm2_createek failed: {result.stderr.decode()}")
        with open("/tmp/ek.pub", "rb") as f:
            return f.read()

    # ------------------------------------------------------------------
    # Attestation quote
    # ------------------------------------------------------------------
    def generate_quote(self, nonce: bytes, pcr_list: list[int]) -> bytes:
        """
        Generate a TPM attestation quote over specified PCRs.
        Returns raw TPM quote blob.
        """
        if not self._available:
            raise RuntimeError("TPM 2.0 not available.")
        pcr_str = ",".join(str(p) for p in pcr_list)
        nonce_hex = nonce.hex()
        result = subprocess.run(
            ["tpm2_quote", "--key-context", "/tmp/ak.ctx",
             "--pcr-list", f"sha256:{pcr_str}",
             "--qualification", nonce_hex,
             "--message", "/tmp/quote.msg",
             "--signature", "/tmp/quote.sig"],
            capture_output=True, timeout=15
        )
        if result.returncode != 0:
            raise RuntimeError(f"tpm2_quote failed: {result.stderr.decode()}")
        with open("/tmp/quote.msg", "rb") as f:
            return f.read()
