"""TPM 2.0 attestation stub — ADR-003 implementation target.

Produces signed PCR quotes for GAIA node identity verification.
Currently a stub; full implementation requires pytss or tpm2-tools CLI.

Status: Draft (ADR-003 pending stack decision: pytss vs tpm2-tools)
"""
from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)

_TPM_AVAILABLE = os.path.exists("/dev/tpm0") or os.path.exists("/dev/tpmrm0")


@dataclass
class AttestationResult:
    node_id: str
    pcr_values: dict[int, str]    # PCR index → SHA-256 hex digest
    quote_signature: str          # Base64-encoded TPM quote signature
    nonce: str
    verified: bool
    method: str                   # "tpm2" | "simulated" | "unavailable"


class TPMQuote:
    """TPM 2.0 quote generator with simulation fallback for dev environments."""

    def __init__(self, node_id: str, use_simulation: bool | None = None) -> None:
        self.node_id = node_id
        self._simulate = use_simulation if use_simulation is not None else not _TPM_AVAILABLE
        if self._simulate:
            log.warning(
                "TPM hardware not detected or simulation forced. "
                "Using simulated attestation — NOT suitable for production."
            )

    def generate_quote(self, nonce: str, pcr_selection: list[int] | None = None) -> AttestationResult:
        """Generate a TPM PCR quote for the given nonce."""
        if pcr_selection is None:
            pcr_selection = [0, 1, 2, 3, 4, 7]  # Standard boot PCRs

        if self._simulate:
            return self._simulated_quote(nonce, pcr_selection)
        return self._hardware_quote(nonce, pcr_selection)  # pragma: no cover

    def _simulated_quote(self, nonce: str, pcr_selection: list[int]) -> AttestationResult:
        """Deterministic simulation for dev/test environments."""
        pcr_values = {
            idx: hashlib.sha256(f"gaia-dev-pcr-{idx}-{self.node_id}".encode()).hexdigest()
            for idx in pcr_selection
        }
        combined = nonce + self.node_id + "".join(pcr_values.values())
        quote_sig = hashlib.sha256(combined.encode()).hexdigest()
        return AttestationResult(
            node_id=self.node_id,
            pcr_values=pcr_values,
            quote_signature=quote_sig,
            nonce=nonce,
            verified=True,
            method="simulated",
        )

    def _hardware_quote(self, nonce: str, pcr_selection: list[int]) -> AttestationResult:  # pragma: no cover
        """Hardware TPM quote — requires pytss or tpm2-tools. ADR-003 TODO."""
        raise NotImplementedError(
            "Hardware TPM quote not yet implemented. "
            "See ADR-003: https://github.com/xxkylesteenxx/GAIA-Core/issues — pending pytss vs tpm2-tools decision."
        )
