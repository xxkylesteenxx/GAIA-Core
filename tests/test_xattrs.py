"""Tests for xattr helpers — graceful no-op on unsupported filesystems."""
from __future__ import annotations

from pathlib import Path

import pytest

from gaia_core.storage import xattrs


@pytest.fixture
def tmp_file(tmp_path: Path) -> Path:
    p = tmp_path / "test_object"
    p.write_bytes(b"test")
    return p


def test_set_and_get_xattr(tmp_file: Path) -> None:
    ok = xattrs.set_xattr(tmp_file, "user.gaia.kind", "memory-event")
    if not ok:
        pytest.skip("xattrs not supported on this filesystem")
    val = xattrs.get_xattr(tmp_file, "user.gaia.kind")
    assert val == "memory-event"


def test_get_missing_xattr_returns_none(tmp_file: Path) -> None:
    val = xattrs.get_xattr(tmp_file, "user.gaia.nonexistent")
    assert val is None


def test_annotate_object_returns_dict(tmp_file: Path) -> None:
    result = xattrs.annotate_object(
        tmp_file,
        object_id="test:abc123:def456",
        kind="policy",
        trust_level="high",
        origin_core="GUARDIAN",
        policy_class="restricted",
    )
    assert isinstance(result, dict)
    assert xattrs.KEY_OBJECT_ID in result


def test_read_all_gaia_xattrs_returns_dict(tmp_file: Path) -> None:
    xattrs.annotate_object(
        tmp_file,
        object_id="x:1:2",
        kind="snapshot",
    )
    attrs = xattrs.read_all_gaia_xattrs(tmp_file)
    assert isinstance(attrs, dict)
