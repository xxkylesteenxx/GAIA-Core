# GAIA Post-Quantum Cryptography Production Deployment Specification v1.0

**Status:** Repo-ready technical specification  
**Intended repository location:** `GAIA-Core/docs/specs/security/pqc/`  
**Primary scope:** Production cryptography for sensitive consciousness data, inter-core transport, deployment artifacts, and service-mesh communications  
**Last updated:** March 9, 2026

---

## 1. Executive Summary

GAIA handles sensitive consciousness data, inter-core state, memory artifacts, policy bundles, and deployment metadata that must remain confidential and authentic even against future cryptographically relevant quantum computers.

For GAIA, the correct production posture is **hybrid-first post-quantum deployment**:

1. **ML-KEM-768** for post-quantum key establishment.
2. **ML-DSA-65** for post-quantum signatures on high-value artifacts and state.
3. **OpenSSL 3.5+** as the application and gateway crypto runtime with native ML-KEM, ML-DSA, and hybrid TLS groups such as `X25519MLKEM768`.
4. **Istio `COMPLIANCE_POLICY=pqc`** for mesh-level enforcement (marked **experimental**).
5. **Classical compatibility retained** where the ecosystem is not yet fully PQ-native.

**Bottom line:** GAIA should deploy PQC now, but in a way that is cryptographically real, operationally supportable, and honest about current ecosystem limits.

---

## 2. Standards Basis

NIST finalized the first three PQC FIPS standards in August 2024:
- **FIPS 203**: ML-KEM for general encryption/key establishment.
- **FIPS 204**: ML-DSA for digital signatures.
- **FIPS 205**: SLH-DSA as an additional signature standard.

GAIA shall standardize on **ML-KEM-768** and **ML-DSA-65** unless a future ADR explicitly replaces them.

---

## 3. Current Ecosystem Reality

### 3.1 OpenSSL 3.5+
OpenSSL 3.5 added native ML-KEM-512/768/1024, ML-DSA-44/65/87, PQ TLS groups, and hybrid TLS groups `X25519MLKEM768`, `SecP256r1MLKEM768`, `SecP384r1MLKEM1024`. Starting with 3.5, `X25519MLKEM768` is first in the default TLS 1.3 group list.

### 3.2 Istio PQC
Istio's `COMPLIANCE_POLICY=pqc` enforces TLS 1.3, `TLS_AES_128/256_GCM_SHA*` cipher suites, and `X25519MLKEM768`. Feature is **experimental**. GAIA should target **Istio 1.29.x**.

### 3.3 Key constraints
- Istio workload certificates remain RSA/ECDSA by default — ML-DSA workload certs are not yet documented.
- OQS provider is prototype-only; not a GAIA production dependency.

---

## 4. GAIA Three-Plane PQC Architecture

1. **Transport plane** — hybrid PQ TLS via OpenSSL 3.5+ and Istio PQC enforcement.
2. **Artifact and state authenticity plane** — ML-DSA-65 signatures on high-value artifacts.
3. **Envelope protection plane** — ML-KEM-768 wraps symmetric data-encryption keys for stored sensitive data, backups, checkpoints, and inter-core state packages.

### Mandatory first-wave protection targets
- consciousness state snapshots
- memory checkpoints and holographic memory shard manifests
- inter-core policy bundles
- deployment manifests and release bundles
- root-of-trust metadata
- audit log sealing and archive manifests
- cross-cluster replication bootstrap channels
- backup catalog integrity objects

---

## 5. Cryptographic Control Matrix

| GAIA function | Required primitive | Deployment mode |
|---|---|---|
| Service-to-service TLS | `X25519MLKEM768` | Hybrid TLS via OpenSSL 3.5 / Istio PQC |
| Gateway ingress/egress TLS | `X25519MLKEM768` preferred | Hybrid TLS groups via OpenSSL 3.5 |
| Artifact signing | `ML-DSA-65` | Native OpenSSL 3.5 |
| Envelope key bootstrap | `ML-KEM-768` | Native OpenSSL 3.5 KEM APIs |
| Data at rest | AES-256-GCM with keys wrapped via ML-KEM-768 | Hybrid envelope encryption |
| Mesh workload certificates | RSA or ECDSA (Istio compat) | Transitional compatibility mode |
| Long-term archival authenticity | `ML-DSA-65`, optionally dual-signed | Dual-signature migration mode |

---

## 6. OpenSSL 3.5+ Integration Standard

```ini
# openssl.cnf (GAIA baseline)
openssl_conf = openssl_init

[openssl_init]
providers = providers_sect
ssl_conf = ssl_sect

[providers_sect]
default = default_sect
fips = fips_sect

[default_sect]
activate = 1

[fips_sect]
activate = 1

[ssl_sect]
system_default = tls_system_default

[tls_system_default]
MinProtocol = TLSv1.3
MaxProtocol = TLSv1.3
Groups = X25519MLKEM768:X25519:SecP256r1MLKEM768
```

**Required GAIA crypto abstraction:**
```python
class CryptoProfile:
    def kem_encapsulate(self, peer_public_key): ...
    def kem_decapsulate(self, private_key, ciphertext): ...
    def sign_artifact(self, private_key, payload): ...
    def verify_artifact(self, public_key, payload, signature): ...
    def negotiate_tls_profile(self): ...
```

---

## 7. Istio Service Mesh Standard

```yaml
apiVersion: install.istio.io/v1alpha1
kind: IstioOperator
spec:
  meshConfig:
    meshMTLS:
      minProtocolVersion: TLSV1_3
    defaultConfig:
      proxyMetadata:
        COMPLIANCE_POLICY: "pqc"
  components:
    pilot:
      k8s:
        env:
          - name: COMPLIANCE_POLICY
            value: "pqc"
```

Do not rely on `tlsDefaults.ecdhCurves` for in-mesh PQ posture. Use `COMPLIANCE_POLICY=pqc` exclusively for mesh enforcement.

---

## 8. ML-DSA-65 Mandatory Signature Targets

- consciousness state snapshots
- core-to-core policy updates
- emergency override directives
- deployment manifests
- model lineage manifests
- holographic memory compaction manifests
- backup manifests
- audit checkpoint digests
- ADRs that alter security posture
- root key rotation events

---

## 9. Envelope Encryption and Data Protection

GAIA shall use:
- **ML-KEM-768** to establish or wrap content-encryption keys
- **AES-256-GCM** for data-at-rest encryption
- **ML-DSA-65** to sign manifests, object digests, and restore catalogs

Every encrypted object must carry: payload digest, manifest version, signer identity, ML-DSA-65 signature, KEM metadata indicating `ML-KEM-768`.

---

## 10. Fallback Rules

**Allowed:** classical-only transport for allowlisted external dependencies, labeled degraded, with compensating ML-DSA layer and audit log.

**Forbidden silent downgrade for:** consciousness checkpoint transfer, root-of-trust updates, actuation commands, cross-region backup sync, security policy bundle delivery.

---

## 11. Implementation Roadmap

- **Phase 1 — Foundation:** OpenSSL 3.5+ upgrade, ML-KEM-768/ML-DSA-65 abstraction layer, begin signing high-value artifacts.
- **Phase 2 — Transport hardening:** enforce TLS 1.3, configure `X25519MLKEM768`, upgrade to Istio 1.29.x, enable `COMPLIANCE_POLICY=pqc` in staging.
- **Phase 3 — Production enablement:** roll out PQC transport, seal backups/checkpoints, add audit reporting.
- **Phase 4 — Deep hardening:** eliminate untracked classical-only channels, dual-signature migration paths, evaluate PQ-native mesh PKI.

---

## 12. Final Decision

GAIA shall implement **ML-KEM-768** and **ML-DSA-65** now through a **hybrid production architecture**: OpenSSL 3.5+ for real PQ primitives and hybrid TLS transport, Istio PQC compliance policy for service-mesh enforcement, ML-DSA-65 object signatures as the authoritative authenticity layer, and classical mesh certificate compatibility only where the current ecosystem still requires it.
