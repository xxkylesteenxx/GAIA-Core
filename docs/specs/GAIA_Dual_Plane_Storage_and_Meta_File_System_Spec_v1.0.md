# GAIA Dual-Plane Storage and Meta-Filesystem Specification v1.0

**Status:** Draft  
**Owner:** GAIA-Core  
**Date:** 2026-03-15  
**Applies to:** GAIA-Core, GAIA-Desktop, GAIA-Server, GAIA-IoT, GAIA-Laptop, GAIA-Meta

---

## 1. Motivation

The original GAIA substrate used a flat single-plane persistence layout:

```
.gaia_state/
  identity/root.json
  memory/events.jsonl
  checkpoints/
```

This is adequate for initial bootstrapping but provides no mechanism for:
- content-addressed object storage
- semantic metadata (provenance, trust, ontology type)
- per-core / per-tenant / per-trust projection views
- a meta-filesystem surface that the FUSE daemon can serve

This spec defines the dual-plane storage architecture that remedies all four gaps.

---

## 2. Expanded State Root Layout

```
.gaia_state/
  identity/          -- IdentityRoot (unchanged)
  memory/            -- CausalMemoryLog (unchanged)
  checkpoints/       -- CheckpointStore (unchanged)
  objects/           -- Plane A: raw content-addressed object store
    <2-char-shard>/
      <sha256-hex>   -- raw bytes, immutable once written
  semantic/          -- Plane B: semantic index and manifests
    index.jsonl      -- append-only SemanticRecord log
  views/             -- Projection plane: mount points / FUSE manifests
```

---

## 3. Plane A — Substrate (Object Store)

### 3.1 Content addressing

Every object is stored under its SHA-256 hash with 2-character directory sharding
(identical to Git's loose object layout).  Content is immutable once written.

### 3.2 Object kinds

| Kind | Description |
|---|---|
| `identity` | Identity root records |
| `memory-event` | Causal memory log entries |
| `checkpoint` | Serialised checkpoint blobs |
| `model-blob` | Model weights and binaries |
| `sensor-artifact` | Raw inbound sensor data |
| `snapshot` | System state snapshots |
| `policy` | Policy documents |
| `manifest` | Distribution or build manifests |
| `semantic-record` | Semantic index snapshots |

### 3.3 xattr annotations (inode-local)

Every object file receives these extended attributes at write time:

| xattr key | Namespace | Content |
|---|---|---|
| `user.gaia.object_id` | user | `<kind>:<hash16>:<uid8>` |
| `user.gaia.kind` | user | ObjectKind value |
| `trusted.gaia.trust_level` | trusted | `standard` / `high` / `verified` |
| `trusted.gaia.origin_core` | trusted | Originating core name |
| `security.gaia.policy_class` | security | MAC policy label |

xattrs are compact inode-local labels only.  They MUST NOT store full
JSON semantic records; that is Plane B's responsibility.

---

## 4. Plane B — Semantic Index

### 4.1 SemanticRecord fields

```json
{
  "object_id": "memory-event:a3f1b2c4d5e6f708:ab12cd34",
  "kind": "memory-event",
  "ontology_type": "gaia:causal-event",
  "provenance_chain": ["<parent-oid>"],
  "causal_parents": ["<parent-oid>"],
  "embedding_refs": [],
  "retrieval_tags": ["grounding", "sensor-fusion"],
  "actuation_constraints": [],
  "tenant_id": null,
  "node_id": "node-001",
  "core_scope": "GROUNDING",
  "trust_level": "standard",
  "extra": {}
}
```

### 4.2 Backing store evolution path

| Phase | Backend |
|---|---|
| v1.0 (now) | Append-only JSONL file (`semantic/index.jsonl`) |
| v1.1 | SQLite with FTS5 for tag search |
| v2.0 | Graph DB (e.g. Kuzu) for provenance traversal |

---

## 5. Projection Plane

### 5.1 Virtual path conventions

```
/gaia/views/by-core/<CORE_NAME>/
/gaia/views/by-trust/high/
/gaia/views/by-kind/<KIND>/
/gaia/views/by-tenant/<TENANT_ID>/
/gaia/views/by-tag/<TAG>/
/gaia/views/by-planetary-state/
```

### 5.2 ProjectionPolicy semantics

- Predicates within a field use **OR** semantics.
- Predicates across fields use **AND** semantics.
- Empty predicate lists match any value (wildcard).
- Deny gates are evaluated before allow filters.

### 5.3 FUSE daemon (future — platform/filesystem/meta_overlay/)

The FUSE daemon will mount the projection plane at `/gaia/views` and:
1. Call `NamespaceViewRegistry.enumerate_view(view_id)` to list visible objects.
2. Serve file content from `ObjectSubstrate.get_bytes(oid)`.
3. Serve per-file metadata from `SemanticIndex.get(oid)`.
4. Expose xattr reads by proxying `xattrs.read_all_gaia_xattrs()` on
   the backing object file.

### 5.4 OverlayFS role (optional)

OverlayFS may be used for `lowerdir=immutable-corpus / upperdir=live-state`
layering to give snapshot-friendly behavior.  It is a union mechanism only;
semantics and reasoning remain in Plane B and the projection layer.

---

## 6. Cross-Repo Consumption Contract

| Repo | How it consumes the dual-plane substrate |
|---|---|
| **GAIA-Core** | Owns and initialises both planes in `bootstrap.py` |
| **GAIA-Desktop** | Calls `build_default_gaia()` → reads view registry for SOPHIA/researcher/HUD views |
| **GAIA-Server** | Calls `build_default_gaia()` → mounts tenant-scoped views |
| **GAIA-IoT** | Calls `get_object_substrate()` → writes sensor artifacts with xattr + semantic record |
| **GAIA-Laptop** | Calls `build_default_gaia()` → uses Core views, no local dual-plane addition |
| **GAIA-Meta** | Federates object IDs, trust metadata, lineage summaries — NOT raw files |

**Rule:** No distribution repo adds its own dual-plane implementation.  All
consume the Core-owned substrate via the `gaia_core.bootstrap` and
`gaia_core.storage` APIs.

---

## 7. Module Index

```
gaia_core/storage/
  __init__.py            -- existing
  contracts.py           -- existing
  etcd_registry.py       -- existing
  jetstream_log.py       -- existing
  minio_store.py         -- existing
  replay_bootstrap.py    -- existing
  object_id.py           -- NEW: ObjectID, ObjectKind
  xattrs.py              -- NEW: inode-local xattr helpers
  semantic_index.py      -- NEW: SemanticRecord, SemanticIndex
  projection_policy.py   -- NEW: ProjectionPolicy, built-in presets
  namespace_views.py     -- NEW: ViewDefinition, NamespaceViewRegistry
  substrate.py           -- NEW: ObjectSubstrate (dual-plane write path)
```

---

## 8. Test Coverage Requirements

| Test file | What it covers |
|---|---|
| `tests/test_storage_substrate.py` | ObjectSubstrate put/get round-trip, sharding, dedup |
| `tests/test_xattrs.py` | annotate_object, read_all_gaia_xattrs, graceful fallback |
| `tests/test_semantic_index.py` | SemanticIndex put/get/query, JSONL persistence, thread safety |
| `tests/test_projection_policy.py` | Policy match/deny logic, preset policies |
| `tests/test_namespace_views.py` | build_standard_views, enumerate_view, resolve_object |
| `tests/test_bootstrap_dual_plane.py` | build_default_gaia creates all six subdirs |
