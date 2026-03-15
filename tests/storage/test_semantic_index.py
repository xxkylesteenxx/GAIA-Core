"""Tests for SemanticIndex."""
from __future__ import annotations
import pytest
from gaia_core.storage.semantic_index import SemanticIndex, SemanticRecord
from gaia_core.storage.object_id import ObjectKind


@pytest.fixture
def index(tmp_path):
    return SemanticIndex(tmp_path / "semantic")


def test_put_and_get(index):
    rec = SemanticRecord(
        object_id="abc123",
        kind=ObjectKind.BLOB.value,
        tags=["test"],
        trust_level="high",
    )
    index.put(rec)
    result = index.get("abc123")
    assert result is not None
    assert result.object_id == "abc123"


def test_filter_by_tag(index):
    rec = SemanticRecord(
        object_id="tag-test",
        kind=ObjectKind.BLOB.value,
        tags=["sensor", "grounding"],
        trust_level="verified",
    )
    index.put(rec)
    results = index.filter(tags=["grounding"])
    assert any(r.object_id == "tag-test" for r in results)


def test_filter_by_trust(index):
    rec = SemanticRecord(
        object_id="trust-test",
        kind=ObjectKind.BLOB.value,
        tags=[],
        trust_level="high",
    )
    index.put(rec)
    results = index.filter(trust_level="high")
    assert any(r.object_id == "trust-test" for r in results)


def test_index_persists_to_disk(tmp_path):
    idx = SemanticIndex(tmp_path / "sem")
    rec = SemanticRecord(object_id="persist", kind="blob", tags=[], trust_level="low")
    idx.put(rec)
    idx2 = SemanticIndex(tmp_path / "sem")
    assert idx2.get("persist") is not None


def test_len(index):
    assert len(index) == 0
    index.put(SemanticRecord(object_id="x", kind="blob", tags=[], trust_level="low"))
    assert len(index) == 1
