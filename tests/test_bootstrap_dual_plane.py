"""Verify build_default_gaia initialises the full dual-plane state layout."""
from __future__ import annotations

from pathlib import Path

import pytest

from gaia_core.bootstrap import build_default_gaia, get_object_substrate


def test_build_default_gaia_creates_all_dirs(tmp_path: Path) -> None:
    state_root = tmp_path / ".gaia_state"
    build_default_gaia(root=state_root)

    for subdir in ("identity", "memory", "checkpoints", "objects", "semantic", "views"):
        assert (state_root / subdir).is_dir(), f"Missing: {subdir}"


def test_get_object_substrate_standalone(tmp_path: Path) -> None:
    from gaia_core.storage.substrate import ObjectSubstrate
    substrate = get_object_substrate(tmp_path / "state")
    assert isinstance(substrate, ObjectSubstrate)
    assert (tmp_path / "state" / "objects").is_dir()
