"""FAISS HNSW hot-tier index service.

Maintains an in-memory HNSW index over MemoryAtom embeddings.
FAISS is an optional dependency — guarded import.

Fallback: linear scan over stored embeddings if FAISS not available.

Usage:
    svc = FaissHnswService(dim=1536)
    svc.add(atom)
    results = svc.search(query_embedding, k=10)
"""
from __future__ import annotations

import logging
import math
import time
from typing import TYPE_CHECKING

from gaia_core.memory.contracts import MemoryAtom, MemorySearchResult

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)

try:
    import faiss  # type: ignore
    import numpy as np  # type: ignore
    _FAISS_AVAILABLE = True
except ImportError:
    faiss = None  # type: ignore
    np = None  # type: ignore
    _FAISS_AVAILABLE = False


class FaissHnswService:
    """Hot-tier FAISS HNSW index over MemoryAtom embeddings."""

    def __init__(self, dim: int = 1536, m: int = 32, ef_construction: int = 200) -> None:
        self.dim = dim
        self._atoms: dict[str, MemoryAtom] = {}   # atom_id -> atom
        self._id_map: list[str] = []               # faiss int index -> atom_id

        if _FAISS_AVAILABLE:
            self._index = faiss.IndexHNSWFlat(dim, m)
            self._index.hnsw.efConstruction = ef_construction
            self._index.hnsw.efSearch = 64
            log.info("FaissHnswService initialised (dim=%d, M=%d, FAISS native)", dim, m)
        else:
            self._index = None
            self._fallback_vecs: list[list[float]] = []
            log.warning("FAISS not available — using linear scan fallback (install faiss-cpu)")

    def add(self, atom: MemoryAtom) -> None:
        """Add a MemoryAtom to the hot index. Requires atom.embedding to be populated."""
        if not atom.embedding:
            raise ValueError(f"MemoryAtom {atom.atom_id} has no embedding — run ingestion pipeline first")
        if len(atom.embedding) != self.dim:
            raise ValueError(f"Embedding dim {len(atom.embedding)} != index dim {self.dim}")
        self._atoms[atom.atom_id] = atom
        if _FAISS_AVAILABLE and self._index is not None:
            import numpy as np
            vec = np.array([atom.embedding], dtype=np.float32)
            faiss.normalize_L2(vec)
            self._index.add(vec)
            self._id_map.append(atom.atom_id)
        else:
            self._fallback_vecs.append(atom.embedding)
            self._id_map.append(atom.atom_id)

    def search(self, query: list[float], k: int = 10) -> list[MemorySearchResult]:
        """Return top-k nearest MemoryAtoms by cosine similarity."""
        if not self._atoms:
            return []
        t0 = time.monotonic()
        k = min(k, len(self._atoms))

        if _FAISS_AVAILABLE and self._index is not None:
            import numpy as np
            qvec = np.array([query], dtype=np.float32)
            faiss.normalize_L2(qvec)
            distances, indices = self._index.search(qvec, k)
            results = []
            for dist, idx in zip(distances[0], indices[0]):
                if idx < 0 or idx >= len(self._id_map):
                    continue
                atom_id = self._id_map[idx]
                atom = self._atoms.get(atom_id)
                if atom:
                    results.append(MemorySearchResult(
                        atom=atom, score=float(dist),
                        tier="hot", latency_ms=(time.monotonic() - t0) * 1000,
                    ))
            return results
        else:
            return self._linear_scan(query, k, t0)

    def _cosine(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(x * x for x in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def _linear_scan(self, query: list[float], k: int, t0: float) -> list[MemorySearchResult]:
        scored = [
            (self._cosine(query, vec), atom_id)
            for vec, atom_id in zip(self._fallback_vecs, self._id_map)
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            MemorySearchResult(
                atom=self._atoms[aid], score=score,
                tier="hot", latency_ms=(time.monotonic() - t0) * 1000,
            )
            for score, aid in scored[:k]
            if aid in self._atoms
        ]

    def size(self) -> int:
        return len(self._atoms)

    def rebuild(self, atoms: list[MemoryAtom]) -> None:
        """Rebuild the index from scratch from a list of atoms."""
        self._atoms.clear()
        self._id_map.clear()
        if _FAISS_AVAILABLE and self._index is not None:
            self._index.reset()
        else:
            self._fallback_vecs.clear()
        for atom in atoms:
            self.add(atom)
        log.info("FaissHnswService rebuilt: %d atoms", len(self._atoms))
