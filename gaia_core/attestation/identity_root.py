"""
GAIA ADR-006 — Unified IdentityRoot Interface
Selects TPM 2.0 backend if available; falls back to software backend.
Exposes a clean interface unchanged from Phase 1 stubs.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass, field
from typing import Optional
from .tpm2_backend import TPM2Backend
from .software_backend import SoftwareBackend

log = logging.getLogger(__name__)


@dataclass
class IdentityRoot:
    """
    GAIA node identity root.
    Wraps TPM2Backend (preferred) or SoftwareBackend (fallback).
    256-bit root bound to hardware or ECDSA key material.
    """
    node_id: str
    force_software: bool = False
    _backend: object = field(default=None, init=False, repr=False)
    _root: Optional[bytes] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        tpm = TPM2Backend()
        if not self.force_software and tpm.available:
            self._backend = tpm
            log.info("[IdentityRoot] Using TPM 2.0 backend.")
        else:
            self._backend = SoftwareBackend()
            log.info("[IdentityRoot] Using software (ECDSA P-256) backend.")
        self._root = self._backend.derive_identity_root(self.node_id)

    @property
    def root_bytes(self) -> bytes:
        """Raw 256-bit identity root."""
        return self._root

    @property
    def root_hex(self) -> str:
        """Hex-encoded identity root for logging/storage."""
        return self._root.hex()

    @property
    def backend_type(self) -> str:
        return "tpm2" if isinstance(self._backend, TPM2Backend) else "software"

    def generate_quote(self, nonce: bytes, pcr_list: list[int] | None = None) -> bytes:
        """Delegate attestation quote generation to active backend."""
        if pcr_list is None:
            pcr_list = [0, 1, 7]  # GAIA default: firmware, boot, secure boot
        return self._backend.generate_quote(nonce, pcr_list)

    def __repr__(self) -> str:
        return f"IdentityRoot(node_id={self.node_id!r}, backend={self.backend_type}, root={self.root_hex[:16]}...)"
