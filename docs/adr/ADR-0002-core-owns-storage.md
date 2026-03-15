# ADR-0002: GAIA-Core Owns the Storage Substrate; Distros Consume

**Date:** 2026-03-15
**Status:** Accepted

## Context

All five distribution repos (Desktop, Laptop, Server, IoT, Meta) already call
`build_default_gaia()` from `gaia_core.bootstrap`. The risk of adding
dual-plane storage independently in each distro repo was identified as a
primary source of future divergence.

## Decision

GAIA-Core is the single owner of the dual-plane storage substrate.
Distribution repos:
- **Must not** implement their own storage plane
- **Must** consume `gaia_core.bootstrap.build_default_gaia()` or
  `gaia_core.bootstrap.get_object_substrate()` for all substrate access
- **May** register additional projection views on top of the Core-provided
  `NamespaceViewRegistry` for their specific needs (tenant views, HUD views, etc.)

GAIA-Meta federates object IDs, trust metadata, and lineage summaries across
nodes — not raw files.

## Consequences

- Positive: zero drift between distros on storage fundamentals
- Positive: semantic index evolution (JSONL → SQLite → graph) happens in one place
- Negative: distros cannot independently evolve storage without a Core PR
- Mitigation: `get_object_substrate()` helper gives distros direct access
  without full substrate init, reducing coupling for IoT/lightweight cases

## References

- ADR-0001
- `gaia_core/bootstrap.py`
- `docs/specs/GAIA_Dual_Plane_Storage_and_Meta_File_System_Spec_v1.0.md` §6
