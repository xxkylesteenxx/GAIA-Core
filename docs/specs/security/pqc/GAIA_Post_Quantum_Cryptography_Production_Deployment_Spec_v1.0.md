# GAIA Post-Quantum Cryptography Production Deployment Spec v1.0

## Status
Draft v1.0

## Objective
Define a deployable GAIA baseline for post-quantum cryptography in production systems, with separate controls for transport, artifact signing, secret wrapping, and compliance evidence.

## Normative baseline
- GAIA SHALL use NIST-standardized PQC primitives for new production baselines where software support exists.
- GAIA SHALL treat transport migration and signing migration as separate tracks.
- GAIA SHALL prefer hybrid TLS supported groups during ecosystem transition.
- GAIA SHALL preserve classical symmetric encryption for payload confidentiality within KEM-based envelope designs.

## 1. Transport
OpenSSL 3.5+ is the user-space reference baseline. The `openssl.cnf` profile in this pack enforces TLS 1.3 and prefers `X25519MLKEM768` while retaining classical fallback groups.

## 2. Signing
Internal artifact signing uses ML-DSA-65 over a canonical manifest. The signed manifest binds file name, size, SHA-256 digest, signer, time, and profile.

## 3. Key establishment and wrapping
ML-KEM-768 is used only to encapsulate a symmetric content-encryption key or a shared secret from which such a key is derived. Payload encryption remains AES-256-GCM or another approved symmetric primitive.

## 4. Mesh integration
Istio overlays in this pack encode GAIA's policy posture and TLS hardening. They do not claim that every Envoy/Istio build natively exposes OpenSSL 3.5 PQ group semantics. Platform teams MUST verify actual data-plane capabilities before asserting PQ transport coverage.

## 5. Auditability
Static checks, policy docs, ADRs, and JSON audit records form the minimum evidence bundle for a PQC production rollout.

## 6. Non-goals
This specification does not define public Internet certificate interoperability or claim that PQC certificate signatures are universally accepted across all clients.
