"""Tests for gaia_core.storage.adapters.overlay_runtime."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from gaia_core.storage.adapters.overlay_runtime import (
    OverlayRuntime,
    SnapshotRecord,
    SystemPlaneWriteError,
)


@pytest.fixture
def runtime(tmp_path):
    return OverlayRuntime(tmp_path)


@pytest.fixture
def unlocked_runtime(tmp_path):
    return OverlayRuntime(tmp_path, lock_system_plane=False)


def test_planes_created(tmp_path):
    OverlayRuntime(tmp_path)
    assert (tmp_path / "system").is_dir()
    assert (tmp_path / "data").is_dir()
    assert (tmp_path / "checkpoints").is_dir()


def test_write_goes_to_data(runtime, tmp_path):
    runtime.write("hello.txt", b"world")
    assert (tmp_path / "data" / "hello.txt").read_bytes() == b"world"
    assert not (tmp_path / "system" / "hello.txt").exists()


def test_read_data_plane(runtime):
    runtime.write("r.txt", b"read me")
    assert runtime.read("r.txt") == b"read me"


def test_read_falls_through_to_system(unlocked_runtime, tmp_path):
    unlocked_runtime.write_system("sys.txt", b"system content")
    assert unlocked_runtime.read("sys.txt") == b"system content"


def test_data_shadows_system(unlocked_runtime):
    unlocked_runtime.write_system("f.txt", b"system")
    unlocked_runtime.write("f.txt", b"data")
    assert unlocked_runtime.read("f.txt") == b"data"


def test_read_missing_returns_none(runtime):
    assert runtime.read("does_not_exist.txt") is None


def test_write_system_locked(runtime):
    with pytest.raises(SystemPlaneWriteError):
        runtime.write_system("secret.txt", b"blocked")


def test_write_system_unlocked(unlocked_runtime, tmp_path):
    unlocked_runtime.write_system("ok.txt", b"allowed")
    assert (tmp_path / "system" / "ok.txt").read_bytes() == b"allowed"


def test_exists(runtime):
    assert not runtime.exists("nope.txt")
    runtime.write("yes.txt", b"1")
    assert runtime.exists("yes.txt")


def test_plane_for(unlocked_runtime):
    unlocked_runtime.write_system("a.txt", b"s")
    unlocked_runtime.write("b.txt", b"d")
    assert unlocked_runtime.plane_for("a.txt") == "system"
    assert unlocked_runtime.plane_for("b.txt") == "data"
    assert unlocked_runtime.plane_for("c.txt") is None


def test_snapshot_system_plane(unlocked_runtime, tmp_path):
    unlocked_runtime.write_system("core.py", b"# system file")
    snap = unlocked_runtime.snapshot_system_plane("initial seal")
    assert snap.file_count == 1
    assert len(snap.root_hash) == 64
    assert snap.plane == "system"


def test_snapshot_index_persisted(unlocked_runtime, tmp_path):
    unlocked_runtime.write_system("x.txt", b"x")
    snap = unlocked_runtime.snapshot_system_plane()
    snaps = unlocked_runtime.list_snapshots()
    assert len(snaps) == 1
    assert snaps[0].snapshot_id == snap.snapshot_id


def test_verify_system_plane_pass(unlocked_runtime):
    unlocked_runtime.write_system("stable.txt", b"unchanged")
    snap = unlocked_runtime.snapshot_system_plane()
    assert unlocked_runtime.verify_system_plane(snap) is True


def test_verify_system_plane_fail(unlocked_runtime, tmp_path):
    unlocked_runtime.write_system("mutable.txt", b"original")
    snap = unlocked_runtime.snapshot_system_plane()
    # Tamper with the system plane directly (bypassing the runtime)
    (tmp_path / "system" / "mutable.txt").write_bytes(b"tampered")
    assert unlocked_runtime.verify_system_plane(snap) is False


def test_list_data_and_system(unlocked_runtime):
    unlocked_runtime.write("d1.txt", b"d")
    unlocked_runtime.write_system("s1.txt", b"s")
    data_files = list(unlocked_runtime.list_data())
    sys_files = list(unlocked_runtime.list_system())
    assert any(f.name == "d1.txt" for f in data_files)
    assert any(f.name == "s1.txt" for f in sys_files)
