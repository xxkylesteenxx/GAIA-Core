# Architecture Decision Record Index

This index lists all ADRs for GAIA-Core in chronological order.
Each ADR captures a significant architectural decision, the context that
drove it, the options considered, and the decision made.

## Status Legend

| Status | Meaning |
|---|---|
| `Proposed` | Under discussion, not yet adopted |
| `Accepted` | Decision made and in effect |
| `Superseded` | Replaced by a later ADR |
| `Deprecated` | No longer relevant |

## ADR Template

```markdown
# ADR-NNNN: Short Title

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Superseded | Deprecated
**Supersedes:** ADR-XXXX (if applicable)

## Context
<!-- What situation forced this decision? -->

## Decision
<!-- What was decided? -->

## Options Considered
<!-- What alternatives were evaluated? -->

## Consequences
<!-- What are the positive and negative outcomes? -->

## References
<!-- Links to specs, issues, PRs, external documents -->
```

## ADR List

| ID | Title | Status | Date |
|---|---|---|---|
| [ADR-0001](ADR-0001-dual-plane-storage.md) | Adopt dual-plane storage substrate in GAIA-Core | Accepted | 2026-03-15 |
| [ADR-0002](ADR-0002-core-owns-storage.md) | GAIA-Core owns storage substrate; distros consume | Accepted | 2026-03-15 |
