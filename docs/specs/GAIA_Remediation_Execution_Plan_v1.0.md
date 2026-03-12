# GAIA Remediation Execution Plan v1.0

## Purpose

Turn the observed repo failures into an ordered repair sequence that maximizes integration progress per patch.

---

## 1. Observed Test Matrix

### 1.1 Standalone

| Repo | Result | Primary issue |
|---|---:|---|
| GAIA-Core | 37 passed, 2 failed | semantic self-model string mismatch in `tests/self/test_identity.py` |
| GAIA-Meta | 15 passed | clean |
| GAIA-IoT | import error | missing packaged `gaia_core` dependency |
| GAIA-Desktop | import errors | missing `gaia_core`; stale `GaiaDesktop` test surface |
| GAIA-Laptop | import error | missing `gaia_core` |
| GAIA-Server | import errors | missing `gaia_core`; `etcd3` imported too early |

### 1.2 Workspace with Core on `PYTHONPATH`

| Repo | Result | Primary issue |
|---|---:|---|
| GAIA-IoT | 12 passed | packaging fixed the surface |
| GAIA-Desktop | 1 collection error, then runtime failures in node tests | entrypoint drift; memory API mismatch |
| GAIA-Laptop | import error | illegal Desktop dependency |
| GAIA-Server | multiple collection errors | inference/storage contract drift; optional dependency side effects |

---

## 2. Highest-Leverage Patch Order

### Phase 1 — Packaging Baseline

**Goal:** make all repos install and import deterministically.

1. Add `pyproject.toml` to IoT, Desktop, Laptop, Meta.
2. Declare `gaia-core` as dependency where required.
3. Add CI workflow to each repo.

**Expected outcome:** IoT should become green quickly; Desktop/Laptop/Server will expose true contract issues instead of packaging noise.

---

### Phase 2 — Core Public Contract Surface

**Goal:** make downstream imports legal.

1. Export `CheckpointRef`, `EventEnvelope`, `StorageBackend` from `gaia_core.storage`.
2. Reconcile inference contract in `gaia_core.inference.contracts`.
3. Document or adapt the continuity memory write method.

**Expected outcome:** Server and Desktop stop failing on avoidable root-export mismatches.

---

### Phase 3 — Desktop Repair

**Goal:** make Desktop internally coherent.

1. Delete or rewrite stale `tests/test_desktop.py` that expects `GaiaDesktop` if `GaiaDesktopNode` is the canonical entrypoint.
2. Replace `substrate.memory.record(...)` with canonical call to `append(...)`, or add a thin compatibility adapter in Core if justified.
3. Re-run Desktop tests in standalone + workspace mode.

**Expected outcome:** Desktop becomes a valid reusable distribution, not a drifting prototype.

---

### Phase 4 — Laptop Boundary Repair

**Goal:** remove cross-repo implementation leakage.

1. Remove `gaia_desktop.*` imports from Laptop.
2. Extract shared dashboard/journal/model-runner support into an authorized shared surface.
3. Re-run Laptop tests.

**Expected outcome:** Laptop becomes independently installable and no longer inherits Desktop's private architecture.

---

### Phase 5 — Server Repair

**Goal:** restore substrate-aligned server behavior.

1. Make `gaia_server.storage.__init__` lazy and side-effect free.
2. Align Server inference/router tests to canonical Core inference types.
3. Validate storage contract roundtrips against Core exports.
4. Fix software-stub PQC verification semantics so tests reflect reality.

**Expected outcome:** Server contract tests become meaningful and reproducible without external services.

---

### Phase 6 — Core Semantic Cleanup

**Goal:** resolve the two remaining Core test failures.

Observed mismatch:
- one test forbids the word `domination` in the response string,
- another test expects `domination` to appear in boundary text.

This is not a packaging defect. It is an internal semantics/wording inconsistency in the self-model layer and should be repaired after repo-boundary stability is restored.

---

## 3. Repo-Specific Repair Notes

### 3.1 GAIA-IoT

This repo is the clearest proof that the packaging pass is worth doing first. With Core available, IoT passed cleanly. That indicates the internal node logic is already coherent enough to move forward.

### 3.2 GAIA-Desktop

Desktop currently has two problems layered together:

1. stale entrypoint expectations,
2. real runtime mismatch between journal code and Core memory API.

So Desktop is partly a stale-test problem and partly a genuine contract problem.

### 3.3 GAIA-Laptop

Laptop is not just missing dependencies. It is violating repo boundaries by importing Desktop internals directly. That must be treated as an architecture violation, not a convenience shortcut.

### 3.4 GAIA-Server

Server has the densest integration surface and therefore needs the most careful normalization:

- Core inference mismatch
- Core storage export mismatch
- eager optional dependency import
- PQC test-stub inconsistency

### 3.5 GAIA-Meta

Meta is already relatively clean. Once Core/Server packaging and contract surfaces are stabilized, Meta should be retested in workspace integration but does not appear to be the immediate bottleneck.

---

## 4. Definition of Done

The remediation pass is complete when:

1. all repos are installable,
2. all repos have CI,
3. IoT, Desktop, Laptop, Server, and Meta have explicit dependency declarations,
4. distribution repos import only authorized public surfaces,
5. Server and Desktop pass on canonical Core contracts,
6. remaining failures are domain-semantic rather than packaging/contract noise.

---

## 5. Recommended Commit Sequence

1. `spec: add cross-repo packaging and dependency policy`
2. `build: add pyproject and ci to all downstream repos`
3. `core: export storage contracts and reconcile inference contract`
4. `desktop: normalize entrypoint and memory API usage`
5. `laptop: remove desktop implementation dependency`
6. `server: make storage imports lazy and align contract tests`
7. `core: resolve self-model wording/test inconsistency`

---

## 6. Final Read

The current system is not blocked by a lack of imagination. It is blocked by the very normal engineering transition from a fast-expanding architecture to a governed multi-repo substrate.

That is good news.

It means the next gains come from discipline, not reinvention.
