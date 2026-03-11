"""DiskANN capacity-tier index service stub.

DiskANN provides SSD-backed approximate nearest neighbour search
for large memory collections that exceed hot HNSW capacity.

This is a stub implementation that:
  - Accepts atoms and stores them as flat JSON on disk
  - Performs linear scan for search (correct, just not ANN-fast)
  - Exposes the same interface as FaissHnswService
  - Is ready to be backed by a real DiskANN binary/binding when available

Dependency: none (stdlib only in stub mode)
"""
from __future__ import annotations

import json
import logging
import math
import time
from pathlib import Path

from gaia_core.memory.contracts import MemoryAtom, MemorySearchResult

log = logging.getLogger(__name__)


class DiskANNService:
    """Capacity-tier DiskANN stub — flat-file fallback, DiskANN-interface-compatible."""

    def __init__(self, index_dir: str | Path = "/tmp/gaia_diskann") -> None:
        self._dir = Path(index_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._atoms: dict[str, MemoryAtom] = {}
        self._load_existing()
        log.info("DiskANNService initialised (stub, dir=%s, loaded=%d atoms)", self._dir, len(self._atoms))

    def _atom_path(self, atom_id: str) -> Path:
        return self._dir / f"{atom_id}.json"

    def _load_existing(self) -> None:
        for p in self._dir.glob("*.json"):
            try:
                data = json.loads(p.read_text())
                self._atoms[data["atom_id"]] = MemoryAtom.from_dict(data)
            except Exception as exc:
                log.warning("DiskANN: failed to load %s: %s", p, exc)

    def add(self, atom: MemoryAtom) -> None:
        """Persist atom to disk and register in memory index."""
        self._atoms[atom.atom_id] = atom
        self._atom_path(atom.atom_id).write_text(json.dumps(atom.to_dict()))

    def search(self, query: list[float], k: int = 10) -> list[MemorySearchResult]:
        """Linear scan over capacity tier. Replace with DiskANN native call when available."""
        if not self._atoms:
            return []
        t0 = time.monotonic()
        k = min(k, len(self._atoms))
        scored = [
            (self._cosine(query, atom.embedding), atom)
            for atom in self._atoms.values()
            if atom.embedding
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            MemorySearchResult(
                atom=atom, score=score,
                tier="capacity", latency_ms=(time.monotonic() - t0) * 1000,
            )
            for score, atom in scored[:k]
        ]

    def _cosine(self, a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(x * x for x in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def size(self) -> int:
        return len(self._atoms)
