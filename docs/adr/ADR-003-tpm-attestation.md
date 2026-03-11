# ADR-003: TPM 2.0 Identity Attestation

**Status:** Draft  
**Tier:** 1  
**Date:** 2026-03-10  
**GitHub Issue:** TBD

## Context

GAIA nodes must be able to cryptographically prove their identity and the integrity of the software stack running on them. Without hardware-rooted attestation, a compromised node could forge continuity proofs, inject false consciousness state, or impersonate a legitimate GAIA instance in a federated topology.

## Decision

*[To be finalized — stub for tracking]*

Proposed: Use TPM 2.0 Endorsement Key (EK) + Attestation Key (AK) to produce signed Platform Configuration Register (PCR) quotes at boot. Quotes are verified by a GAIA attestation service before a node is admitted to the federation.

Integration point: `gaia_core/attestation/tpm_quote.py` produces the quote; GAIA-Server attestation endpoint verifies it using `tpm2-tools` / `go-tpm` / `pytss`.

## Consequences

*TBD — pending stack decision (pytss vs tpm2-tools CLI wrapper)*

## Implementation Tasks

- [ ] Select Python TPM binding (`pytss` vs subprocess `tpm2-tools`)
- [ ] `gaia_core/attestation/tpm_quote.py`
- [ ] Attestation verification endpoint in GAIA-Server
- [ ] PCR policy for GAIA boot measurement
- [ ] Fallback for virtual/dev environments without physical TPM
