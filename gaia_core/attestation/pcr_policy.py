"""
GAIA ADR-006 — PCR Seal/Unseal Policy
Binds identity root to PCR values at boot time for integrity enforcement.
"""
from __future__ import annotations
import hashlib
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

log = logging.getLogger(__name__)

GAIA_DEFAULT_PCRS = [0, 1, 7]  # Firmware, boot config, secure boot state


@dataclass
class PCRPolicy:
    """
    PCR-based seal/unseal policy for GAIA identity root.
    Seals the identity root to a specific set of PCR values;
    unsealing validates the current PCR state matches the sealed policy.
    """
    pcr_indices: List[int] = field(default_factory=lambda: list(GAIA_DEFAULT_PCRS))
    _sealed_digest: Optional[bytes] = field(default=None, init=False, repr=False)
    _pcr_snapshot: Dict[int, bytes] = field(default_factory=dict, init=False, repr=False)

    def seal(self, identity_root: bytes, pcr_values: Dict[int, bytes]) -> bytes:
        """
        Seal identity root to given PCR values.
        Returns sealed digest (SHA-256 of root + concatenated PCR values).
        """
        if set(pcr_values.keys()) != set(self.pcr_indices):
            raise ValueError("PCR values must cover all policy indices.")
        self._pcr_snapshot = dict(pcr_values)
        pcr_concat = b"".join(pcr_values[i] for i in sorted(self.pcr_indices))
        self._sealed_digest = hashlib.sha256(identity_root + pcr_concat).digest()
        log.info(f"[PCRPolicy] Identity root sealed to PCRs {self.pcr_indices}.")
        return self._sealed_digest

    def unseal(self, identity_root: bytes, current_pcr_values: Dict[int, bytes]) -> bool:
        """
        Unseal: verify current PCR values match sealed policy.
        Returns True if boot integrity confirmed; False if tampered.
        """
        if self._sealed_digest is None:
            raise RuntimeError("No sealed digest present. Call seal() first.")
        pcr_concat = b"".join(current_pcr_values[i] for i in sorted(self.pcr_indices))
        candidate = hashlib.sha256(identity_root + pcr_concat).digest()
        result = candidate == self._sealed_digest
        if result:
            log.info("[PCRPolicy] Unseal SUCCESS — boot integrity confirmed.")
        else:
            log.error("[PCRPolicy] Unseal FAILED — PCR mismatch, possible tamper.")
        return result

    def simulate_pcr_values(self, nonce: bytes) -> Dict[int, bytes]:
        """Generate deterministic simulated PCR values (dev/test use only)."""
        return {
            i: hashlib.sha256(nonce + i.to_bytes(1, "big")).digest()
            for i in self.pcr_indices
        }
