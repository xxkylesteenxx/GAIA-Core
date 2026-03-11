"""Tests for FAISS hot index rebuild from atom list."""
from __future__ import annotations

import pytest

from gaia_core.memory.contracts import MemoryAtom
from gaia_core.memory.hot_index.faiss_hnsw_service import FaissHnswService


def _atom(content: str, dim: int = 4) -> MemoryAtom:
    import math
    # Simple unit vector embedding for testing
    vec = [1.0 / math.sqrt(dim)] * dim
    return MemoryAtom(content=content, core="TEST", embedding=vec)


def test_add_and_search():
    svc = FaissHnswService(dim=4)
    atom = _atom("hello world")
    svc.add(atom)
    assert svc.size() == 1
    results = svc.search([0.5, 0.5, 0.5, 0.5], k=1)
    assert len(results) == 1
    assert results[0].atom.atom_id == atom.atom_id


def test_rebuild_restores_index():
    svc = FaissHnswService(dim=4)
    atoms = [_atom(f"memory {i}") for i in range(5)]
    for a in atoms:
        svc.add(a)
    assert svc.size() == 5

    # Rebuild from same atom list
    svc.rebuild(atoms)
    assert svc.size() == 5
    results = svc.search([0.5, 0.5, 0.5, 0.5], k=3)
    assert len(results) == 3


def test_empty_index_returns_no_results():
    svc = FaissHnswService(dim=4)
    results = svc.search([0.5, 0.5, 0.5, 0.5], k=5)
    assert results == []


def test_atom_without_embedding_raises():
    svc = FaissHnswService(dim=4)
    atom = MemoryAtom(content="no embedding", core="TEST")
    with pytest.raises(ValueError, match="no embedding"):
        svc.add(atom)
