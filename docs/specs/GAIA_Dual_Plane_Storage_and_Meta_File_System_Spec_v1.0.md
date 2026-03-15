# GAIA Dual-Plane Storage and Meta-Filesystem Specification

**Version:** 1.0  
**Status:** Active  
**Owner:** GAIA-Core  
**Applies To:** All repos  
**Last Updated:** 2026-03-15

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
  schemas.py               ← canonical type definitions (ObjectMeta, ViewManifest,
                              PlaneLayout, StorageCapability, SemanticRecord re-export)
  object_id.py             ← ObjectID, ObjectKind, generate_object_id()
  substrate.py             ← ObjectSubstrate (dual-plane write/read path)
                              [spec originally listed as object_store.py;
                               object_store.py is now a shim that re-exports
                               ObjectSubstrate as ObjectStore for compat]
  object_store.py          ← thin re-export shim → substrate.ObjectSubstrate
  semantic_index.py        ← SemanticRecord, SemanticIndex
  xattrs.py                ← annotate_object(), inode xattr helpers
  projection_policy.py     ← ProjectionPolicy, filter_records(), built-in policies
  namespace_views.py       ← ViewDefinition, NamespaceViewRegistry, build_standard_views()
  contracts.py             ← abstract base contracts (StorageBackend protocol)
  etcd_registry.py         ← etcd-backed distributed registry adapter
  jetstream_log.py         ← NATS JetStream log adapter
  minio_store.py           ← MinIO S3-compatible object store adapter
  replay_bootstrap.py      ← replay-from-log substrate recovery
  adapters/
    __init__.py            ← re-exports GaiaFuseMount, OverlayRuntime
    fuse_mount.py          ← FUSE daemon: mounts views/ as real filesystem paths
    overlay_runtime.py     ← system/data plane split + snapshot + verification
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
- **`data/` (writable):** all runtime writes are directed here.
- **Read fallthrough:** `read(path)` checks `data/` first, then `system/`.
  This mirrors the macOS firmlink model where the Data volume shadows the
  System volume for user-owned paths.
- **Snapshots:** `snapshot_system_plane()` computes a SHA-256 root hash over
  all files in `system/` and appends a `SnapshotRecord` to
  `checkpoints/snapshots.jsonl`. `verify_system_plane(snap)` detects drift.

---

## 6. Projection Views (`GaiaFuseMount`)

`NamespaceViewRegistry` holds all registered views. `build_standard_views()`
creates the standard GAIA view set:

| View ID | Virtual Prefix | Filter |
|---|---|---|
| `by-trust-high` | `/gaia/views/by-trust/high` | `trust_level = high \| verified` |
| `by-kind-sensor` | `/gaia/views/by-kind/sensor-event` | `kind = sensor-event` |
| `planetary` | `/gaia/views/by-planetary-state` | open (all records) |
| `by-core-<NAME>` | `/gaia/views/by-core/<NAME>` | `core_scope = NAME` |
| `by-tenant-<ID>` | `/gaia/views/by-tenant/<ID>` | `tenant_id = ID` |

`GaiaFuseMount` translates this registry into a real mountpoint (Linux FUSE,
requires `fusepy` or `pyfuse3`). Each object appears as a read-only JSON file
at `/gaia/views/<view-id>/<object-id>`. Raw bytes are accessible at
`/gaia/objects/<shard>/<hash>`.

`GaiaFuseMount.write_manifests(views_dir)` persists one `ViewManifest` JSON
file per view so the FUSE daemon can reconstruct the registry out-of-process.

---

## 7. Type Contracts (`schemas.py`)

| Type | Purpose |
|---|---|
| `SemanticRecord` | Rich metadata for one object (re-exported from `semantic_index`) |
| `ObjectMeta` | Lightweight frozen summary of a stored object (no raw bytes) |
| `ViewManifest` | Serialisable view descriptor; written to `views/*.json` |
| `PlaneLayout` | Typed directory layout contract for `.gaia_state/` |
| `StorageCapability` | Enum of capabilities a substrate node may advertise |

---

## 8. Bootstrap Integration

`gaia_core.bootstrap.build_default_gaia()` initialises the full layout:

```python
object_substrate = ObjectSubstrate(root)          # creates objects/, semantic/, views/
view_registry = build_standard_views(             # registers standard projection views
    index=object_substrate.index,
    core_names=DEFAULT_CORES,
)
```

`OverlayRuntime` and `GaiaFuseMount` are activated by the platform layer at
boot time (not in bootstrap) because they require OS-level capabilities
(FUSE kernel module, write access to `/gaia/views`).

---

## 9. Capability Advertising

A substrate node advertises its active capabilities via `StorageCapability`:

```python
from gaia_core.storage.schemas import StorageCapability

node_caps = {
    StorageCapability.CONTENT_ADDRESSED,
    StorageCapability.SEMANTIC_INDEX,
    StorageCapability.PROJECTION_VIEWS,
    StorageCapability.FUSE_MOUNT,       # set when GaiaFuseMount is active
    StorageCapability.OVERLAY_RUNTIME,  # set when OverlayRuntime is active
    StorageCapability.SNAPSHOT,         # set when checkpoints/ is populated
}
```

---

## 10. Versioning

Breaking changes to the layout contract (directory names, type field names,
write-path semantics) increment the major version of this spec and require
a coordinated update to `SPEC-INDEX.md` and the Fleet Governance Index.
Additive changes (new capability enum values, new view IDs) increment the
minor version.
