"""Tests for ObjectSubstrate dual-plane write/read path."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from gaia_core.storage.object_id import ObjectKind
from gaia_core.storage.substrate import ObjectSubstrate


@pytest.fixture
def substrate(tmp_path: Path) -> ObjectSubstrate:
    return ObjectSubstrate(tmp_path / ".gaia_state")


def test_put_creates_object_file(substrate: ObjectSubstrate) -> None:
    data = b"hello gaia"
    oid = substrate.put(data, ObjectKind.MEMORY_EVENT)
    obj_path = substrate._object_path(oid)
    assert obj_path.exists()
    assert obj_path.read_bytes() == data


def test_put_is_content_addressed(substrate: ObjectSubstrate) -> None:
    data = b"deterministic"
    oid1 = substrate.put(data, ObjectKind.CHECKPOINT)
    oid2 = substrate.put(data, ObjectKind.CHECKPOINT)
    assert oid1.content_hash == oid2.content_hash


def test_get_bytes_round_trip(substrate: ObjectSubstrate) -> None:
    data = b"sensor reading 42"
    oid = substrate.put(data, ObjectKind.SENSOR_ARTIFACT)
    assert substrate.get_bytes(oid) == data


def test_semantic_record_created(substrate: ObjectSubstrate) -> None:
    data = b"policy doc"
    oid = substrate.put(
        data,
        ObjectKind.POLICY,
        ontology_type="gaia:policy",
        trust_level="high",
        core_scope="GUARDIAN",
        retrieval_tags=["governance"],
    )
    record = substrate.get_record(oid)
    assert record is not None
    assert record.trust_level == "high"
    assert record.core_scope == "GUARDIAN"
    assert "governance" in record.retrieval_tags


def test_objects_and_semantic_dirs_created(tmp_path: Path) -> None:
    s = ObjectSubstrate(tmp_path / "state")
    assert (tmp_path / "state" / "objects").is_dir()
    assert (tmp_path / "state" / "semantic").is_dir()
    assert (tmp_path / "state" / "views").is_dir()


def test_sharding(substrate: ObjectSubstrate) -> None:
    oid = substrate.put(b"shard test", ObjectKind.SNAPSHOT)
    obj_path = substrate._object_path(oid)
    # Parent dir name should be the 2-char shard prefix
    assert obj_path.parent.name == oid.content_hash[:2]
