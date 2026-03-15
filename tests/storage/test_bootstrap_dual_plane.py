"""Integration test: dual-plane storage is wired into GaiaSubstrate."""
from __future__ import annotations

import pytest

from gaia_core.bootstrap import build_default_gaia, get_object_substrate
from gaia_core.storage.schemas import PlaneLayout, StorageCapability


@pytest.fixture
def substrate(tmp_path):
    return build_default_gaia(root=tmp_path)


def test_substrate_has_storage(substrate):
    assert substrate.has_storage is True


def test_object_store_field(substrate):
    assert substrate.object_store is not None


def test_view_registry_field(substrate):
    assert substrate.view_registry is not None


def test_view_registry_has_standard_views(substrate):
    view_ids = [v.view_id for v in substrate.view_registry.list_views()]
    assert "by-trust-high" in view_ids
    assert "planetary" in view_ids
    assert "by-core-sophia" in view_ids


def test_storage_capabilities(substrate):
    caps = substrate.storage_capabilities()
    assert StorageCapability.CONTENT_ADDRESSED in caps
    assert StorageCapability.SEMANTIC_INDEX in caps
    assert StorageCapability.PROJECTION_VIEWS in caps


def test_all_plane_dirs_created(substrate, tmp_path):
    layout = PlaneLayout(tmp_path)
    for plane in (
        layout.identity, layout.memory, layout.checkpoints,
        layout.objects, layout.semantic, layout.views,
        layout.system, layout.data,
    ):
        assert plane.is_dir(), f"Expected directory: {plane}"


def test_consciousness_snapshot_includes_storage(substrate):
    snap = substrate.consciousness_snapshot()
    assert "storage" in snap
    assert snap["storage"]["view_count"] > 0
    assert "CONTENT_ADDRESSED" in snap["storage"]["capabilities"]


def test_substrate_without_storage_is_safe():
    """GaiaSubstrate remains constructable without storage fields (backward compat)."""
    from gaia_core.core.registry import CoreRegistry
    from gaia_core.continuity.identity import IdentityRoot
    import tempfile
    from pathlib import Path
    from gaia_core.continuity.causal_memory import CausalMemoryLog
    from gaia_core.continuity.checkpoints import CheckpointStore
    from gaia_core.federation.workspace import CollectiveWorkspace
    from gaia_core.core.substrate import GaiaSubstrate

    with tempfile.TemporaryDirectory() as d:
        p = Path(d)
        identity = IdentityRoot.create()
        registry = CoreRegistry()
        memory = CausalMemoryLog(p / "events.jsonl")
        checkpoints = CheckpointStore(p / "checkpoints")
        workspace = CollectiveWorkspace(
            workspace_id="test",
            problem_frame="test",
            goals=[],
        )
        sub = GaiaSubstrate(
            registry=registry,
            identity=identity,
            memory=memory,
            checkpoints=checkpoints,
            workspace=workspace,
            # no object_store, no view_registry
        )
        assert sub.has_storage is False
        assert sub.storage_capabilities() == []


def test_get_object_substrate(tmp_path):
    store = get_object_substrate(tmp_path)
    assert (tmp_path / "objects").is_dir()
    assert (tmp_path / "semantic").is_dir()
    assert (tmp_path / "views").is_dir()
