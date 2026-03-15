# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| `main` (HEAD) | ✅ Active development |
| Tagged releases | ✅ Until superseded |
| Pre-0.1 commits | ❌ No backports |

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report vulnerabilities privately:

1. **GitHub Private Vulnerability Reporting** (preferred):
   Use the [Security Advisories](../../security/advisories/new) tab in this
   repository to file a private report directly with the maintainers.

2. **Email**: Send details to the maintainer listed in `pyproject.toml`.
   Include:
   - Description of the vulnerability and affected component
   - Steps to reproduce
   - Potential impact assessment
   - Any suggested mitigations (optional)

## Response Timeline

| Stage | Target |
|---|---|
| Acknowledgement | 72 hours |
| Initial triage | 7 days |
| Fix or mitigation | 30 days (critical), 90 days (moderate) |
| Public disclosure | Coordinated with reporter |

## Scope

In scope:
- `gaia_core/` Python substrate
- `.github/workflows/` CI pipeline
- `platform/`, `kernel/`, `vmm/` system-level code
- Dual-plane storage: `gaia_core/storage/`
- Any cryptographic, identity, or trust-chain components

Out of scope:
- Third-party dependencies (report upstream)
- Documentation typos
- Issues in clearly experimental / `WIP` branches

## Disclosure Policy

GAIA follows coordinated disclosure. We will credit reporters in release
notes unless they request anonymity.
