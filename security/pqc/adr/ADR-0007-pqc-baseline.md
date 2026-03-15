# ADR-0007: PQC Baseline

## Status
Accepted

## Context
GAIA requires a production cryptography baseline that addresses harvest-now-decrypt-later risk while staying aligned with currently standardized algorithms and currently deployable software.

## Decision
GAIA adopts the following baseline:
- OpenSSL 3.5+ as the primary user-space crypto runtime.
- ML-KEM-768 as the default internal KEM baseline.
- Hybrid TLS supported-group preference led by `X25519MLKEM768`.
- ML-DSA-65 for internal artifact signing.
- TLS 1.3 only at the control-plane baseline.

## Consequences
- Transport and artifact-signing transitions are staged separately.
- Istio data-plane adoption depends on mesh/runtime capabilities and cannot be assumed to expose OpenSSL-style PQ configuration directly.
- All exceptions require explicit documentation.
