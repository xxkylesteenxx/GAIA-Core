# GAIA Secure Compute and Verification Spec v1.0

**Document Type:** Canonical Technical Specification
**Version:** 1.0
**Date:** 2026-03-14
**Authority:** GAIA Engineering Council
**Applies To:** All GAIA repositories, build pipelines, runtime environments, and node deployments

---

## 1. Purpose

This specification defines the cryptographic, supply-chain, hardware-root-of-trust, and runtime verification requirements for all GAIA compute infrastructure. Its goal is to ensure that every GAIA node runs exactly the code it is supposed to run, that every artifact can be traced to its source, and that compromise of any single node cannot propagate undetected.

---

## 2. Governing Standards

- **NIST SP 800-207** — Zero Trust Architecture
- **NIST SP 800-193** — Platform Firmware Resiliency
- **NIST SSDF (SP 800-218)** — Secure Software Development Framework
- **NIST PQC Standards (FIPS 203/204/205)** — Post-Quantum Cryptography
- **SLSA Framework** — Supply-chain Levels for Software Artifacts
- **in-toto Framework** — Software supply chain integrity
- **SPIFFE/SPIRE** — Secure workload identity
- **TPM 2.0 / TCG specifications** — Hardware root of trust

---

## 3. Supply Chain Integrity

### 3.1 SLSA Compliance Target
All GAIA production artifacts must reach **SLSA Level 3** as a minimum:
- Builds must be hermetic and reproducible
- Build provenance must be generated and signed
- Source must be version controlled with two-party review
- Build service must be non-forgeable

### 3.2 in-toto Policy
All GAIA build pipelines must produce in-toto link metadata at each step:
- source fetch
- dependency resolution
- compilation / packaging
- container image build
- signing
- deployment

The full chain must be verifiable end-to-end before any artifact is admitted to production.

### 3.3 Dependency Management
- All dependencies must be pinned to exact hashes, not version ranges
- Dependency updates must pass automated vulnerability scanning (OSV, GHSA)
- No transitive dependency may be added without explicit review
- Software Bill of Materials (SBOM) must be generated in SPDX or CycloneDX format for every release

---

## 4. Hardware Root of Trust

### 4.1 TPM 2.0 Requirement
All GAIA production nodes must be provisioned with TPM 2.0 or equivalent hardware security module. The TPM must be used for:
- measured boot (PCR attestation)
- sealed storage of node identity keys
- runtime integrity measurement

### 4.2 SPIFFE/SPIRE Workload Identity
All GAIA services must obtain their identity via SPIRE. No service may present a self-signed certificate or static credential as its primary identity in production. SVID rotation must occur at intervals not exceeding 24 hours.

### 4.3 Secure Boot
All GAIA nodes must boot with Secure Boot enabled. The boot chain from firmware to kernel to GAIA userspace must be cryptographically verified at each stage.

---

## 5. Cryptographic Standards

### 5.1 Current Algorithms
| Use Case | Required Algorithm |
|----------|-------------------|
| Symmetric encryption | AES-256-GCM |
| Asymmetric / signatures | Ed25519 or ECDSA P-384 |
| Key exchange | ECDH P-384 or X25519 |
| Hashing | SHA-256 minimum, SHA-3 preferred |
| TLS | 1.3 minimum, 1.2 only with explicit exception |

### 5.2 Post-Quantum Migration
GAIA must maintain a PQC migration roadmap. By 2027:
- All new key exchange must support ML-KEM (FIPS 203)
- All new signature schemes must support ML-DSA (FIPS 204) or SLH-DSA (FIPS 205)
- Hybrid classical+PQC schemes are acceptable during transition

### 5.3 Key Management
- All cryptographic keys must be stored in hardware security modules or TPM-sealed storage
- No plaintext private keys may appear in source code, environment variables, or log files
- Key rotation schedules must be documented and enforced automatically

---

## 6. Runtime Verification

### 6.1 Code Integrity
All GAIA executables and container images must be signed. The runtime must verify signatures before execution. Unsigned code must be rejected.

### 6.2 Memory Safety
- New systems code (kernel modules, VMM, HAL drivers) must be written in Rust unless a specific exception is approved
- Existing C code must pass static analysis (clang-tidy, cppcheck) with zero high-severity findings before deployment
- Address Space Layout Randomization (ASLR) and stack canaries must be enabled on all nodes

### 6.3 Anomaly Detection
- Runtime behavioral anomaly detection must be active on all production nodes
- Unexpected syscall patterns, network connections, or file system mutations must trigger GUARDIAN alerts
- eBPF-based monitoring is the preferred implementation

---

## 7. Zero Trust Network Architecture

- No GAIA service may trust another service based solely on network location
- All service-to-service calls must be mutually authenticated via SPIFFE SVIDs
- Least-privilege network policies must be enforced via Kubernetes NetworkPolicy or equivalent
- All inter-core IPC must be encrypted even within the same node
- East-west traffic between consciousness cores must be logged and auditable

---

## 8. Vulnerability Management

- CVE scanning must run on every build and every 24 hours in production
- Critical CVEs (CVSS 9.0+) must be remediated within 24 hours
- High CVEs (CVSS 7.0–8.9) must be remediated within 7 days
- Medium CVEs must be remediated within 30 days
- All vulnerability findings and remediation timelines must be logged to the GAIA audit ledger

---

## 9. Audit and Compliance

- All security events must be logged to an append-only, tamper-evident audit ledger
- Audit logs must be retained for minimum 1 year
- Quarterly automated compliance checks must validate against this spec
- Annual third-party penetration testing is required for SIL 3/4 deployments
