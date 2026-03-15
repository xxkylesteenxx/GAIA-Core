# GAIA Dual-Plane Storage and Meta-Filesystem Specification

**Version:** 1.0  
**Status:** Active  
**Owner:** GAIA-Core  
**Applies To:** All repos  
**Last Updated:** 2026-03-15  
**Canonical Path:** `docs/specs/storage/`

---

## 1. Purpose

This specification defines the dual-plane storage architecture for the GAIA substrate.
It governs how all persistent objects are stored, annotated, indexed, projected, and
surfaced as filesystem paths across all GAIA distribution targets.

The design benchmarks against two reference OSes at the capability level:

| Capability | macOS APFS reference | Windows NTFS reference | GAIA equivalent |
|---|---|---|---|
| Protected system plane | Sealed System Volume (SSV) | System32 write protection | `system/` plane (write-locked, snapshotted) |
| Writable data plane | Data volume | `%APPDATA%`, user profile | `data/` plane |
| Metadata + policy | Extended attributes | ACLs + alternate data streams | `xattrs.py` + `SemanticRecord` |
| Rollback / snapshot | APFS snapshots | VSS | `OverlayRuntime.snapshot_system_plane()` |
| Projection / indirection | Firmlinks, symlinks | Reparse points | `NamespaceViewRegistry` projection views |

---

## 2. State Directory Layout

```
.gaia_state/
  identity/        ← IdentityRoot (node_id, public key, genesis timestamp)
  memory/          ← CausalMemoryLog (append-only JSONL event stream)
  checkpoints/     ← CheckpointStore + OverlayRuntime snapshot index
  objects/         ← Content-addressed raw object store (2-char sharding)
  semantic/        ← SemanticIndex (JSONL-backed rich metadata plane)
  views/           ← ViewManifest JSON files (one per registered view)
  system/          ← Read-only system plane (sealed by OverlayRuntime)
  data/            ← Writable data plane (all runtime writes go here)
```

`PlaneLayout` in `gaia_core/storage/schemas.py` is the single source of truth
for this directory contract.

---

## 3. Package Structure

```
gaia_core/storage/
  __init__.py              ← public re-exports
  schemas.py               ← ObjectMeta, ViewManifest, PlaneLayout,
                              StorageCapability, SemanticRecord re-export
  object_id.py             ← ObjectID, ObjectKind, generate_object_id()
  substrate.py             ← ObjectSubstrate (dual-plane write/read path)
  object_store.py          ← thin re-export shim → substrate.ObjectSubstrate
  semantic_index.py        ← SemanticRecord, SemanticIndex
  xattrs.py                ← annotate_object(), read_xattrs(), inode helpers
  projection_policy.py     ← ProjectionPolicy, filter_records(), built-in policies
  namespace_views.py       ← ViewDefinition, NamespaceViewRegistry,
                              build_standard_views()
  contracts.py             ← StorageBackend protocol
  etcd_registry.py         ← etcd-backed distributed registry adapter
  jetstream_log.py         ← NATS JetStream log adapter
  minio_store.py           ← MinIO S3-compatible object store adapter
  replay_bootstrap.py      ← replay-from-log substrate recovery
  adapters/
    __init__.py
    fuse_mount.py          ← GaiaFuseMount: FUSE daemon, mounts views/ as VFS
    overlay_runtime.py     ← OverlayRuntime: system/data split + snapshot
```

---

## 4. Dual-Plane Write Path

Every write through `ObjectSubstrate.put()` executes three steps atomically:

1. **Raw bytes → `objects/`** — content-addressed, 2-char git-style sharding
2. **Compact xattrs** — inode-local identity via `xattrs.annotate_object()`
3. **Semantic record → `semantic/`** — rich metadata via `SemanticIndex.put()`

---

## 5. System / Data Plane Split (`OverlayRuntime`)

`OverlayRuntime` enforces a hard separation:

- **`system/` (read-only):** provisioned at substrate bootstrap, write-locked
  by default (`lock_system_plane=True`). The GAIA equivalent of APFS SSV.
- **`data/` (writable):** all runtime writes go here.
- **Read fallthrough:** `read(path)` checks `data/` first, then `system/`.
- **Snapshots:** `snapshot_system_plane()` computes a SHA-256 root hash and
  appends a `SnapshotRecord` to `checkpoints/snapshots.jsonl`.
  `verify_system_plane(snap)` detects drift from the sealed state.

---

## 6. Projection Views (`NamespaceViewRegistry` / `GaiaFuseMount`)

`build_standard_views()` creates the standard GAIA view set:

| View ID | Virtual Prefix | Filter |
|---|---|---|
| `by-trust-high` | `/gaia/views/by-trust/high` | `trust_level = high \| verified` |
| `by-kind-sensor` | `/gaia/views/by-kind/sensor-event` | `kind = sensor-event` |
| `planetary` | `/gaia/views/by-planetary-state` | open (all records) |
| `by-core-<NAME>` | `/gaia/views/by-core/<NAME>` | `core_scope = NAME` |
| `by-tenant-<ID>` | `/gaia/views/by-tenant/<ID>` | `tenant_id = ID` |

`GaiaFuseMount` translates the registry into a real mountpoint (Linux FUSE).
Each object appears as a read-only JSON file at `/gaia/views/<view-id>/<oid>`.

---

## 7. Type Contracts (`schemas.py`)

| Type | Purpose |
|---|---|
| `SemanticRecord` | Rich metadata for one object |
| `ObjectMeta` | Lightweight frozen summary (no raw bytes) |
| `ViewManifest` | Serialisable view descriptor; written to `views/*.json` |
| `PlaneLayout` | Typed directory layout contract for `.gaia_state/` |
| `StorageCapability` | Enum of capabilities a substrate node may advertise |

---

## 8. `GaiaSubstrate` Integration

`build_default_gaia()` wires storage as first-class fields:

```python
substrate = build_default_gaia()
substrate.object_store    # ObjectSubstrate
substrate.view_registry   # NamespaceViewRegistry
substrate.has_storage     # True
substrate.storage_capabilities()  # [CONTENT_ADDRESSED, SEMANTIC_INDEX, PROJECTION_VIEWS]
```

`GaiaSubstrate` accepts both fields as `Optional` so existing callers that
construct the substrate directly continue to work without modification.

---

## 9. Capability Advertising

```python
from gaia_core.storage.schemas import StorageCapability

node_caps = {
    StorageCapability.CONTENT_ADDRESSED,
    StorageCapability.SEMANTIC_INDEX,
    StorageCapability.PROJECTION_VIEWS,
    StorageCapability.FUSE_MOUNT,
    StorageCapability.OVERLAY_RUNTIME,
    StorageCapability.SNAPSHOT,
}
```

---

## 10. Distro Repo Consumption Pattern

All distribution repos (Desktop, Laptop, Server, IoT, Meta) consume storage
through `build_default_gaia()` — they do not instantiate `ObjectSubstrate`
or `NamespaceViewRegistry` directly.

```python
# In any distro repo entrypoint:
from gaia_core.bootstrap import build_default_gaia
substrate = build_default_gaia(root=config.state_dir)
assert substrate.has_storage
```

---

## 11. Versioning

Breaking changes to the layout contract increment the major version of this
spec and require coordinated updates to `SPEC-INDEX.md` and the Fleet
Governance Index. Additive changes increment the minor version.
