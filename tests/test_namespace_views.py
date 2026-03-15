"""Tests for NamespaceViewRegistry and build_standard_views."""
from __future__ import annotations

from pathlib import Path

import pytest

from gaia_core.storage.object_id import ObjectKind
from gaia_core.storage.semantic_index import SemanticIndex, SemanticRecord
from gaia_core.storage.namespace_views import build_standard_views, NamespaceViewRegistry


@pytest.fixture
def index(tmp_path: Path) -> SemanticIndex:
    idx = SemanticIndex(tmp_path / "index.jsonl")
    idx.put(SemanticRecord(
        object_id="oid-1", kind="sensor-artifact",
        core_scope="GROUNDING", trust_level="standard",
    ))
    idx.put(SemanticRecord(
        object_id="oid-2", kind="policy",
        core_scope="GUARDIAN", trust_level="high",
    ))
    idx.put(SemanticRecord(
        object_id="oid-3", kind="memory-event",
        core_scope="SOPHIA", trust_level="standard",
        tenant_id="tenant-abc",
    ))
    return idx


def test_build_standard_views_creates_core_views(index: SemanticIndex) -> None:
    registry = build_standard_views(
        index, core_names=["SOPHIA", "GUARDIAN", "GROUNDING"]
    )
    view_ids = {v.view_id for v in registry.list_views()}
    assert "by-core-sophia" in view_ids
    assert "by-core-guardian" in view_ids


def test_enumerate_view_core_filter(index: SemanticIndex) -> None:
    registry = build_standard_views(index, core_names=["SOPHIA"])
    records = registry.enumerate_view("by-core-sophia")
    assert all(r.core_scope == "SOPHIA" for r in records)
    assert len(records) == 1


def test_enumerate_view_high_trust(index: SemanticIndex) -> None:
    registry = build_standard_views(index)
    records = registry.enumerate_view("by-trust-high")
    assert all(r.trust_level in ("high", "verified") for r in records)


def test_enumerate_view_sensor(index: SemanticIndex) -> None:
    registry = build_standard_views(index)
    records = registry.enumerate_view("by-kind-sensor")
    assert all(r.kind == "sensor-artifact" for r in records)


def test_resolve_object_visible(index: SemanticIndex) -> None:
    registry = build_standard_views(index, core_names=["GUARDIAN"])
    rec = registry.resolve_object("by-core-guardian", "oid-2")
    assert rec is not None
    assert rec.object_id == "oid-2"


def test_resolve_object_not_visible(index: SemanticIndex) -> None:
    registry = build_standard_views(index, core_names=["SOPHIA"])
    # oid-2 belongs to GUARDIAN, not SOPHIA
    rec = registry.resolve_object("by-core-sophia", "oid-2")
    assert rec is None


def test_tenant_view(index: SemanticIndex) -> None:
    registry = build_standard_views(
        index, tenant_ids=["tenant-abc"]
    )
    records = registry.enumerate_view("by-tenant-tenant-abc")
    assert len(records) == 1
    assert records[0].tenant_id == "tenant-abc"
