# Changelog

All notable changes to GAIA-Core are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Dual-plane storage substrate: `gaia_core/storage/` with `object_id`, `xattrs`,
  `semantic_index`, `projection_policy`, `namespace_views`, and `substrate` modules
- `ObjectSubstrate` content-addressed object store with Git-style 2-char sharding
- `SemanticIndex` append-only JSONL-backed rich metadata plane
- `ProjectionPolicy` with OR-within-field / AND-across-fields predicate engine
- `NamespaceViewRegistry` and `build_standard_views()` for per-core/trust/tenant views
- Updated `bootstrap.py` to initialise expanded `.gaia_state/` layout with
  `objects/`, `semantic/`, and `views/` alongside legacy planes
- `get_object_substrate()` module-level helper for distro repos
- Spec: `docs/specs/GAIA_Dual_Plane_Storage_and_Meta_File_System_Spec_v1.0.md`
- Tests: `test_storage_substrate`, `test_xattrs`, `test_namespace_views`,
  `test_bootstrap_dual_plane`
- Community health files: LICENSE, SECURITY.md, CONTRIBUTING.md,
  CODE_OF_CONDUCT.md, CODEOWNERS, issue templates, PR template
- CI workflows: test.yml, release.yml, sbom.yml, provenance.yml

### Changed
- `bootstrap.py`: extended `.gaia_state/` layout; backward-compatible with all
  existing callers

## [0.1.0] - 2026-03-09

### Added
- Initial 8-core registry: SOPHIA, GUARDIAN, ATLAS, NEXUS, GROUNDING,
  INFERENCE, MEMORY, SELF
- `IdentityRoot`, `CausalMemoryLog`, `CheckpointStore`
- `GaiaSubstrate` with `CollectiveWorkspace` federation layer
- `gaia_core/storage/`: `contracts`, `etcd_registry`, `jetstream_log`,
  `minio_store`, `replay_bootstrap`
- Linux kernel, VMM, compositor, HAL, platform, AI orchestration stubs
- Initial docs: ARCHITECTURE.md, DECISIONS.md, GAIA_DNA.md, specs/
