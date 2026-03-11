"""GAIA attestation package — TPM 2.0 identity and boot integrity."""

from gaia_core.attestation.tpm_quote import TPMQuote, AttestationResult

__all__ = ["TPMQuote", "AttestationResult"]
