# ADR-0001: Adopt Dual-Plane Storage Substrate in GAIA-Core

**Date:** 2026-03-15
**Status:** Accepted

## Context

The original `bootstrap.py` initialised a single-plane flat-file store:
`identity/`, `memory/`, `checkpoints/`. This provides no mechanism for
content-addressed object storage, semantic metadata (provenance, trust,
ontology type), per-core or per-tenant projection views, or a FUSE-mountable
meta-filesystem surface.

## Decision

Extend the `.gaia_state/` root with three new planes:
- `objects/` — content-addressed raw object store (SHA-256, Git-style sharding)
- `semantic/` — append-only JSONL semantic index (`SemanticRecord`)
- `views/` — projection mount points consumed by the namespace view registry

Implemented in `gaia_core/storage/`: `object_id`, `xattrs`, `semantic_index`,
`projection_policy`, `namespace_views`, `substrate`.

## Options Considered

1. **Keep flat layout, add metadata inline** — Rejected: breaks content
   addressing and makes semantic queries O(n) file scans.
2. **Use a database only** — Rejected: removes filesystem-native xattr
   provenance and breaks FUSE projection assumptions.
3. **Dual-plane with JSONL index (chosen)** — Accepted: filesystem-native
   for durability, JSONL for queryability now, upgradeable to SQLite/graph.

## Consequences

- Positive: all six repos inherit the dual-plane substrate via `build_default_gaia()`
- Positive: FUSE daemon can be added later without changing the index contract
- Positive: xattrs provide inode-local provenance without index dependency
- Negative: JSONL index is O(n) for large datasets — planned SQLite migration at v1.1

## References

- `docs/specs/GAIA_Dual_Plane_Storage_and_Meta_File_System_Spec_v1.0.md`
- `gaia_core/storage/substrate.py`
- `gaia_core/bootstrap.py`
