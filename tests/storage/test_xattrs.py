"""Tests for xattrs annotation helpers."""
from __future__ import annotations
import pytest
from gaia_core.storage.xattrs import annotate_object, read_xattrs


def test_annotate_creates_sidecar(tmp_path):
    target = tmp_path / "obj.bin"
    target.write_bytes(b"data")
    annotate_object(target, object_id="abc", kind="blob", trust_level="high")
    attrs = read_xattrs(target)
    assert attrs["object_id"] == "abc"
    assert attrs["kind"] == "blob"
    assert attrs["trust_level"] == "high"


def test_read_missing_returns_empty(tmp_path):
    target = tmp_path / "noxattr.bin"
    target.write_bytes(b"x")
    assert read_xattrs(target) == {}


def test_annotate_overwrites(tmp_path):
    target = tmp_path / "obj2.bin"
    target.write_bytes(b"y")
    annotate_object(target, object_id="id1", kind="blob", trust_level="low")
    annotate_object(target, object_id="id1", kind="blob", trust_level="high")
    attrs = read_xattrs(target)
    assert attrs["trust_level"] == "high"
