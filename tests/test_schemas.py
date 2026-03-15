"""Tests for gaia_core.storage.schemas."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from gaia_core.storage.schemas import (
    ObjectMeta,
    PlaneLayout,
    SemanticRecord,
    StorageCapability,
    ViewManifest,
)


def test_semantic_record_reexport():
    rec = SemanticRecord(object_id="test:abc", kind="blob")
    assert rec.object_id == "test:abc"
    assert rec.kind == "blob"


def test_object_meta_frozen():
    meta = ObjectMeta(
        object_id="blob:abc123",
        kind="blob",
        size_bytes=42,
        content_hash="abc123",
    )
    assert meta.size_bytes == 42
    with pytest.raises(Exception):
        meta.size_bytes = 99  # type: ignore[misc]  # frozen


def test_view_manifest_round_trip():
    m = ViewManifest(
        view_id="by-core-SOPHIA",
        virtual_prefix="/gaia/views/by-core/SOPHIA",
        description="SOPHIA objects",
        allowed_cores=["SOPHIA"],
    )
    d = m.to_dict()
    m2 = ViewManifest.from_dict(d)
    assert m2.view_id == m.view_id
    assert m2.allowed_cores == ["SOPHIA"]


def test_view_manifest_write_read(tmp_path):
    m = ViewManifest(
        view_id="test-view",
        virtual_prefix="/gaia/views/test",
    )
    path = m.write(tmp_path)
    assert path.exists()
    m2 = ViewManifest.read(path)
    assert m2.view_id == "test-view"


def test_plane_layout_paths(tmp_path):
    layout = PlaneLayout(tmp_path)
    assert layout.objects == tmp_path / "objects"
    assert layout.semantic == tmp_path / "semantic"
    assert layout.system == tmp_path / "system"
    assert layout.data == tmp_path / "data"


def test_plane_layout_ensure_all(tmp_path):
    layout = PlaneLayout(tmp_path)
    layout.ensure_all()
    for plane in (
        layout.identity, layout.memory, layout.checkpoints,
        layout.objects, layout.semantic, layout.views,
        layout.system, layout.data,
    ):
        assert plane.is_dir()


def test_storage_capability_enum():
    assert StorageCapability.FUSE_MOUNT in StorageCapability
    assert StorageCapability.OVERLAY_RUNTIME in StorageCapability
    caps = list(StorageCapability)
    assert len(caps) == 7
