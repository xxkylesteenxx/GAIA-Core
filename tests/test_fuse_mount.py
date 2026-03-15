"""Tests for gaia_core.storage.adapters.fuse_mount (dry_run mode)."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from gaia_core.storage.adapters.fuse_mount import GaiaFuseMount, _view_to_manifest
from gaia_core.storage.namespace_views import build_standard_views
from gaia_core.storage.semantic_index import SemanticIndex
from gaia_core.storage.schemas import ViewManifest


@pytest.fixture
def index(tmp_path):
    return SemanticIndex(tmp_path / "semantic" / "index.jsonl")


@pytest.fixture
def registry(index):
    return build_standard_views(index=index, core_names=["SOPHIA", "GUARDIAN"])


@pytest.fixture
def fuse(registry, tmp_path):
    return GaiaFuseMount(
        registry=registry,
        objects_dir=tmp_path / "objects",
        dry_run=True,
    )


def test_list_view_ids(fuse):
    ids = fuse.list_view_ids()
    assert "by-trust-high" in ids
    assert "by-core-sophia" in ids
    assert "planetary" in ids


def test_enumerate_view_empty(fuse):
    records = fuse.enumerate_view("planetary")
    assert isinstance(records, list)


def test_resolve_object_missing(fuse):
    assert fuse.resolve_object("planetary", "nonexistent") is None


def test_mount_dry_run(fuse):
    # Should not raise, should not touch the filesystem
    fuse.mount()
    assert not fuse._mounted


def test_record_to_file_content(fuse):
    from gaia_core.storage.semantic_index import SemanticRecord
    rec = SemanticRecord(object_id="blob:abc", kind="blob", ontology_type="gaia:test")
    content = fuse.record_to_file_content(rec)
    parsed = json.loads(content)
    assert parsed["object_id"] == "blob:abc"


def test_write_manifests(fuse, tmp_path):
    views_dir = tmp_path / "views"
    paths = fuse.write_manifests(views_dir)
    assert len(paths) > 0
    for p in paths:
        assert p.exists()
        m = ViewManifest.read(p)
        assert m.view_id
        assert m.virtual_prefix.startswith("/gaia/views/")


def test_load_manifests_round_trip(fuse, tmp_path):
    views_dir = tmp_path / "views"
    fuse.write_manifests(views_dir)
    manifests = fuse.load_manifests(views_dir)
    ids_written = set(fuse.list_view_ids())
    ids_loaded = {m.view_id for m in manifests}
    assert ids_written == ids_loaded


def test_object_path(fuse, tmp_path):
    h = "abcdef1234567890" * 2
    p = fuse.object_path(h)
    assert p.parts[-2] == h[:2]
    assert p.parts[-1] == h


def test_view_to_manifest_fields():
    from gaia_core.storage.namespace_views import ViewDefinition
    from gaia_core.storage.projection_policy import ProjectionPolicy
    from gaia_core.storage.semantic_index import SemanticIndex
    import tempfile, pathlib
    with tempfile.TemporaryDirectory() as d:
        idx = SemanticIndex(pathlib.Path(d) / "idx.jsonl")
        vd = ViewDefinition(
            view_id="test",
            virtual_prefix="/gaia/views/test",
            index=idx,
            policy=ProjectionPolicy(name="test", allowed_cores=["NEXUS"]),
        )
        m = _view_to_manifest(vd)
        assert m.view_id == "test"
        assert m.allowed_cores == ["NEXUS"]
