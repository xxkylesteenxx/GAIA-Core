"""Tests for NamespaceViewRegistry and build_standard_views."""
from __future__ import annotations
import pytest
from gaia_core.storage.semantic_index import SemanticIndex, SemanticRecord
from gaia_core.storage.namespace_views import build_standard_views, NamespaceViewRegistry
from gaia_core.storage.object_id import ObjectKind


@pytest.fixture
def registry(tmp_path):
    index = SemanticIndex(tmp_path / "semantic")
    return build_standard_views(index=index, core_names=["SOPHIA", "GUARDIAN", "ATLAS"])


def test_standard_views_registered(registry):
    ids = [v.view_id for v in registry.list_views()]
    assert "by-trust-high" in ids
    assert "planetary" in ids
    assert "by-core-sophia" in ids
    assert "by-core-guardian" in ids


def test_view_count(registry):
    views = registry.list_views()
    # by-trust-high, by-kind-sensor, planetary, by-core-* x3 = 6 minimum
    assert len(views) >= 6


def test_query_empty_view_returns_empty(registry):
    results = registry.query("planetary")
    assert results == []


def test_query_populated_view(tmp_path):
    index = SemanticIndex(tmp_path / "sem")
    reg = build_standard_views(index=index, core_names=["MEMORY"])
    rec = SemanticRecord(
        object_id="v-test",
        kind=ObjectKind.BLOB.value,
        tags=[],
        trust_level="high",
    )
    index.put(rec)
    results = reg.query("by-trust-high")
    assert any(r.object_id == "v-test" for r in results)


def test_unknown_view_raises(registry):
    with pytest.raises((KeyError, ValueError)):
        registry.query("nonexistent-view")
