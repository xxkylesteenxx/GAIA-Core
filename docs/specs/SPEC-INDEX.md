# GAIA-Core Specification Index

This index is the authoritative registry of all formal specifications
that govern GAIA-Core and its distribution repos.

## Index Format

| Spec ID | Title | Status | Version | Applies To |
|---|---|---|---|---|
| SPEC-001 | Dual-Plane Storage and Meta-Filesystem | Active | 1.0 | All repos |
| SPEC-002 | Energy Optimization | Active | 1.0 | Core, Laptop, IoT |
| SPEC-003 | Environmental Data Quality | Active | 1.0 | Core, IoT |
| SPEC-004 | Inter-Process Communication | Active | 1.0 | Core |
| SPEC-005 | Linux Kernel Modifications | Active | 1.0 | Core |
| SPEC-006 | Planetary Multi-Agent Coordination | Active | 1.0 | Meta, Core |
| SPEC-007 | Post-Quantum Cryptography | Active | 1.0 | All repos |
| SPEC-008 | Remediation Execution Plan | Active | 1.0 | All repos |
| SPEC-009 | Synergy Measurement Framework | Active | 1.0 | All repos |
| SPEC-010 | Virtualization and Core Isolation | Active | 1.0 | Core |
| SPEC-011 | Python Orchestration | Active | 1.0 | Core |
| SPEC-012 | Virtual Memory and IPC | Active | 1.0 | Core |

## Spec Lifecycle

```
Draft → Review → Active → Deprecated
```

- **Draft**: Under authorship, not yet binding
- **Review**: Open for comment from all repo maintainers
- **Active**: Binding on all named repos in "Applies To"
- **Deprecated**: Superseded by a newer spec (link provided)

## Filing a New Spec

1. Copy an existing spec as template
2. Assign the next SPEC-NNN ID in this index
3. Open a PR with both the spec file and this index updated
4. Spec becomes Active only after PR is merged to `main`

## Cross-Repo Governance

Specs that apply to multiple repos are filed in GAIA-Core `docs/specs/`
and referenced (not duplicated) in each distro repo's `docs/` directory.
GAIA-Meta maintains the fleet-level governance index at
`GAIA-Meta/docs/specs/GAIA_Fleet_Governance_Index_v1.0.md`.
