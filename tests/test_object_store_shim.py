"""Tests for the object_store shim module."""
from __future__ import annotations

from gaia_core.storage import object_store
from gaia_core.storage.object_store import ObjectStore, ObjectSubstrate
from gaia_core.storage.substrate import ObjectSubstrate as SubstrateObjectSubstrate


def test_object_store_shim_identity():
    assert ObjectStore is SubstrateObjectSubstrate
    assert ObjectSubstrate is SubstrateObjectSubstrate


def test_object_store_shim_usable(tmp_path):
    store = ObjectStore(tmp_path)
    assert (tmp_path / "objects").is_dir()
    assert (tmp_path / "semantic").is_dir()
    assert (tmp_path / "views").is_dir()
