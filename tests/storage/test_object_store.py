"""Tests for ObjectSubstrate (content-addressed dual-plane store)."""
from __future__ import annotations
import pytest
from gaia_core.storage.substrate import ObjectSubstrate
from gaia_core.storage.object_id import ObjectKind


@pytest.fixture
def store(tmp_path):
    return ObjectSubstrate(tmp_path)


def test_put_and_get_roundtrip(store):
    oid = store.put(b"hello world", kind=ObjectKind.BLOB)
    assert store.get(oid) == b"hello world"


def test_objects_dir_created(store, tmp_path):
    assert (tmp_path / "objects").is_dir()


def test_semantic_dir_created(store, tmp_path):
    assert (tmp_path / "semantic").is_dir()


def test_views_dir_created(store, tmp_path):
    assert (tmp_path / "views").is_dir()


def test_object_is_content_addressed(store):
    oid1 = store.put(b"same", kind=ObjectKind.BLOB)
    oid2 = store.put(b"same", kind=ObjectKind.BLOB)
    assert oid1 == oid2


def test_different_content_different_id(store):
    oid1 = store.put(b"aaa", kind=ObjectKind.BLOB)
    oid2 = store.put(b"bbb", kind=ObjectKind.BLOB)
    assert oid1 != oid2


def test_get_missing_returns_none(store):
    assert store.get("nonexistent-id") is None


def test_index_records_put(store):
    oid = store.put(b"indexed", kind=ObjectKind.BLOB)
    records = list(store.index)
    assert any(r.object_id == oid for r in records)
