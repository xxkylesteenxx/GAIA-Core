# GAIA Cross-Repo Packaging and Dependency Resolution Spec v1.0

## Boundary Compliance Header

**Document ID:** GAIA-SPEC-PKG-001  
**Title:** Cross-Repo Packaging and Dependency Resolution Spec v1.0  
**Status:** Draft v1.0  
**Authority Layer:** Engineering Systems / Repository Architecture  
**Primary Authority Owner:** GAIA-Core for shared contracts; each distribution repo for implementation-local modules  
**Scope Tier:** Tier 1 enabling spec  
**In Scope:** packaging, import boundaries, workspace development, CI, version compatibility, optional dependency hygiene, public export surfaces  
**Out of Scope:** kernel internals, model quality, GUI design, consciousness validation theory weights, production networking topology  
**Primary Inputs:** uploaded repo snapshots; executed local test matrix across Core, Server, IoT, Desktop, Laptop, Meta  
**Primary Output:** a deterministic multi-repo development and release model that removes hidden local-path assumptions and contract ambiguity

---

## 1. Purpose

GAIA now exists as a multi-repository system rather than a single monorepo-like scaffold. That makes packaging and dependency governance load-bearing.

This spec defines the rules required for all GAIA repositories to:

1. install deterministically,
2. import only authorized contract surfaces,
3. test in both standalone and workspace modes,
4. publish stable compatibility expectations, and
5. prevent cross-repo implementation bleed.

Without this layer, downstream failures present as random `ModuleNotFoundError`, stale tests, or interface drift. Those are symptoms of missing repository governance, not just missing code.

---

## 2. Current Defect Map

Observed from the uploaded snapshots and direct test execution.

### 2.1 Standalone execution state

| Repo | Standalone result | Meaning |
|---|---:|---|
| GAIA-Core | partial pass | core runs, but contains 2 semantic self-model test failures |
| GAIA-Meta | pass | cleanest downstream package |
| GAIA-IoT | fail | fails only because `gaia_core` is unavailable |
| GAIA-Desktop | fail | missing `gaia_core`, plus stale/outdated test surface |
| GAIA-Laptop | fail | missing `gaia_core`, then imports Desktop internals |
| GAIA-Server | fail | missing `gaia_core`; optional dependency import side effects; contract drift |

### 2.2 Workspace execution state with `GAIA-Core` on `PYTHONPATH`

| Repo | Workspace result | Primary blocker |
|---|---:|---|
| GAIA-IoT | pass | packaging only |
| GAIA-Desktop | fail | test/import drift and memory API mismatch |
| GAIA-Laptop | fail | illegal dependency on `gaia_desktop.*` |
| GAIA-Server | fail | inference contract drift, storage export drift, optional dependency import side effects |

### 2.3 Concrete defects

1. `GAIA-IoT` imports `gaia_core` directly and has no packaging declaration for it.
2. `GAIA-Desktop` has two incompatible test surfaces:
   - `tests/test_desktop.py` expects `GaiaDesktop`
   - implementation exports `GaiaDesktopNode`
3. `GAIA-Desktop` interaction journal calls `substrate.memory.record(...)`, while GAIA-Core provides `CausalMemoryLog.append(...)`.
4. `GAIA-Laptop` imports:
   - `gaia_desktop.dashboard.server.DashboardServer`
   - `gaia_desktop.interaction.journal.InteractionJournal`
   - `gaia_desktop.models.runner.LocalModelRunner`
5. `GAIA-Server` expects `RuntimeBackend` and `TaskType` from `gaia_core.inference.contracts`, but current Core exports a different contract surface.
6. `GAIA-Server` imports `CheckpointRef` and `EventEnvelope` from `gaia_core.storage`, but Core does not export those from `gaia_core.storage.__init__`.
7. `GAIA-Server` storage package imports `etcd3` at package import time through `gaia_server.storage.__init__`, causing even configuration-only tests to fail when optional backends are absent.
8. Only `GAIA-Core` and `GAIA-Server` currently ship `pyproject.toml` in the uploaded snapshots.
9. Only `GAIA-Core` currently exposes a visible CI workflow in the uploaded snapshots.

---

## 3. Normative Decisions

### 3.1 Packaging mode

All GAIA repositories **MUST** support two execution modes:

#### A. Standalone package mode
The repository installs by itself via:

```bash
pip install -e .
```

This mode is required for:
- repo-local unit tests,
- linting,
- packaging validation,
- import contract enforcement.

#### B. Workspace integration mode
The repository installs alongside other GAIA repos in a controlled workspace.

This mode is required for:
- cross-repo integration tests,
- local development across repos,
- compatibility verification before release.

No repository may assume that sibling directories happen to exist unless the documented workspace bootstrap explicitly installs them.

### 3.2 Shared substrate ownership

`GAIA-Core` **MUST** be the sole owner of shared substrate contracts used across multiple distributions.

These include at minimum:
- inference contracts,
- storage contracts,
- restore contracts,
- continuity/memory interfaces,
- causal/event envelopes,
- serialization helpers,
- attestation-facing abstractions.

A distribution repo **MUST NOT** become the accidental owner of a cross-repo contract simply because another repo imports one of its modules.

### 3.3 Distribution isolation rule

Distribution repos **MUST NOT** import one another's implementation internals.

Forbidden examples:
- Laptop importing Desktop dashboard internals
- IoT importing Server-specific storage backends
- Desktop importing Meta orchestration internals

Allowed examples:
- Desktop importing GAIA-Core public contracts
- Laptop importing a separately published shared UI/support package
- Meta importing GAIA-Core and GAIA-Server public integration surfaces if explicitly declared

### 3.4 Public export rule

If downstream code is expected to import a type from a package root, that type **MUST** be exported from that package root.

Examples:
- `from gaia_core.storage import CheckpointRef` is valid only if `gaia_core/storage/__init__.py` exports it.
- Tests and docs must not rely on deep imports when the architecture expects a stable top-level public surface.

### 3.5 Optional dependency rule

Optional backends **MUST NOT** be imported at package import time.

Heavy or environment-bound modules such as:
- `etcd3`
- MinIO clients
- JetStream/NATS clients
- hardware sensor libraries
- GUI servers

must be loaded lazily in factories or backend-specific modules.

A config-only import must not trigger a backend import explosion.

---

## 4. Canonical Dependency Topology

### 4.1 Repo graph

```text
GAIA-Core
├── shared substrate contracts
├── continuity / restore / storage / inference / governance abstractions
└── base runtime substrate

GAIA-Server -> GAIA-Core
GAIA-IoT    -> GAIA-Core
GAIA-Desktop-> GAIA-Core
GAIA-Laptop -> GAIA-Core
GAIA-Meta   -> GAIA-Core (+ explicitly declared Server integration if needed)
```

### 4.2 Forbidden graph edges

```text
GAIA-Laptop  -X-> GAIA-Desktop implementation internals
GAIA-Desktop -X-> GAIA-Laptop implementation internals
GAIA-IoT     -X-> GAIA-Desktop implementation internals
GAIA-Server  -X-> Desktop/Laptop implementation internals
```

### 4.3 Shared-support extraction rule

If two or more distribution repos require the same non-Core utility, that code **MUST** be moved to one of the following:

1. `GAIA-Core`, only if the capability is substrate-level,
2. a new dedicated shared package, such as `gaia_shared_ui` or `gaia_edge_common`, if the capability is not substrate-level.

Laptop reusing Desktop dashboard code directly is therefore non-compliant.

---

## 5. Required Packaging Baseline Per Repo

Each repo **MUST** contain:

1. `pyproject.toml`
2. package metadata with name/version
3. Python version floor
4. base dependencies
5. optional dependency groups/extras
6. test dependencies
7. importable top-level package
8. at least one CI workflow running tests

### 5.1 Minimum package metadata

Each `pyproject.toml` should define:

- package name
- version
- description
- requires-python
- dependencies
- optional-dependencies
- test tool configuration

### 5.2 Extras model

Recommended extras pattern:

- `server[storage]` → etcd3, minio, nats/jetstream clients
- `desktop[ui]` → dashboard/UI dependencies
- `desktop[models]` → local model runtime clients
- `iot[sensors]` → hardware-specific sensor packages
- `meta[federation]` → optional distributed coordination clients

This keeps base installs light and importable.

---

## 6. Public Contract Surfaces

The following roots are designated public and stable once exported:

### 6.1 `gaia_core.inference`
Owns canonical inference request/response/backend/task abstractions.

### 6.2 `gaia_core.storage`
Owns storage-neutral contracts including:
- `CheckpointRef`
- `EventEnvelope`
- `StorageBackend`

### 6.3 `gaia_core.restore`
Owns restore manifest and restore-path abstractions.

### 6.4 `gaia_core.continuity`
Owns continuity interfaces including causal memory append semantics.

### 6.5 `gaia_core.utils.serialization`
Owns wire-format helpers used by downstream repos.

Any cross-repo import outside these public surfaces must be treated as suspect until explicitly authorized.

---

## 7. CI and Test Matrix

### 7.1 Required CI in every repo

Every repo **MUST** run, at minimum:

1. package install
2. unit tests
3. import-boundary checks
4. smoke import of top-level package

### 7.2 Required integration matrix

A separate workspace job **MUST** validate the following combinations:

- Core + IoT
- Core + Desktop
- Core + Laptop
- Core + Server
- Core + Server + Meta

### 7.3 Boundary enforcement checks

CI **MUST** fail if:

- Laptop imports `gaia_desktop.*`
- Desktop imports `gaia_laptop.*`
- a repo imports undeclared optional backends at package import time
- downstream code imports a type from a package root that the root does not export

### 7.4 Test taxonomy

Tests should be tagged into:

- `unit`: repo-local, standalone
- `contract`: uses GAIA-Core public types only
- `integration`: workspace, multi-repo
- `optional`: requires external services or extras

---

## 8. Versioning and Compatibility

### 8.1 Versioning rule

GAIA repos **SHOULD** use semver-like compatibility signaling even if still pre-1.0.

Recommended form:
- Core: `0.x.y`
- downstream repos declare a compatible Core window, e.g. `>=0.2,<0.3`

### 8.2 Compatibility matrix

A machine-readable compatibility file **SHOULD** be maintained, for example:

```yaml
core: 0.2.x
server:
  requires_core: ">=0.2,<0.3"
iot:
  requires_core: ">=0.2,<0.3"
desktop:
  requires_core: ">=0.2,<0.3"
laptop:
  requires_core: ">=0.2,<0.3"
meta:
  requires_core: ">=0.2,<0.3"
  requires_server: ">=0.2,<0.3"
```

### 8.3 Contract change rule

A shared contract change in Core **MUST** trigger:

1. contract tests in Core,
2. downstream compatibility tests,
3. explicit changelog entry for breaking or deprecated fields.

---

## 9. Immediate Remediation Actions

### 9.1 Packaging baseline

1. Add `pyproject.toml` to IoT, Desktop, Laptop, Meta.
2. Define `gaia-core` as a dependency where required.
3. Create CI workflows in all repos.

### 9.2 Contract export fixes in Core

1. Export `CheckpointRef`, `EventEnvelope`, and `StorageBackend` from `gaia_core.storage`.
2. Finalize the canonical inference contract and export it from `gaia_core.inference`.
3. Document the continuity/memory write API.

### 9.3 Desktop repair

1. Remove or update stale `GaiaDesktop` test surface.
2. Normalize the public entrypoint name.
3. Replace `substrate.memory.record(...)` with the canonical Core memory API.

### 9.4 Laptop repair

1. Remove direct imports from `gaia_desktop.*`.
2. Move shared dashboard/journal/model-runner code into an authorized shared surface.
3. Re-test in standalone and workspace modes.

### 9.5 Server repair

1. Stop importing optional storage backends in `gaia_server.storage.__init__`.
2. Align `gaia_server` to the canonical Core inference contract.
3. Depend only on exported Core storage contract roots.

---

## 10. Acceptance Criteria

This spec is satisfied only when all of the following are true:

1. Every repo installs with `pip install -e .`.
2. Every repo has a working CI workflow.
3. IoT passes standalone or documented-core workspace mode according to declared policy.
4. Desktop passes without stale entrypoint tests and without memory API mismatch.
5. Laptop passes without importing Desktop internals.
6. Server contract tests pass against GAIA-Core public exports.
7. Optional dependency absence does not break config-only or contract-only test imports.
8. A workspace integration matrix passes for all declared combinations.

---

## 11. Risks if Not Adopted

If this spec is not enforced, GAIA will continue to present the following failure pattern:

- downstream repos appear "almost working" but only inside one developer's local filesystem layout,
- integration bugs are discovered late and look random,
- tests become stale proxies for architecture that no longer exists,
- repo count increases faster than trust in repo boundaries,
- the system drifts from open-source engineering discipline into coordination theater.

---

## 12. Final Decision

GAIA is now beyond the stage where informal sibling imports are acceptable.

From this point forward:

- `GAIA-Core` owns shared contracts,
- distribution repos own only their local implementation,
- shared non-Core capabilities must be extracted intentionally,
- optional services are loaded lazily,
- every repo is installable, testable, and CI-governed.

That is the minimum substrate required for the next layer of specs to mean anything operationally.
