"""Hot-tier query router.

Routes search requests across available hot-tier index shards
and merges results by score.
"""
from __future__ import annotations

import logging
from gaia_core.memory.contracts import MemoryAtom, MemorySearchResult
from gaia_core.memory.hot_index.faiss_hnsw_service import FaissHnswService

log = logging.getLogger(__name__)


class HotRouter:
    """Routes queries across one or more FaissHnswService shards."""

    def __init__(self) -> None:
        self._shards: dict[str, FaissHnswService] = {}

    def add_shard(self, name: str, shard: FaissHnswService) -> None:
        self._shards[name] = shard
        log.info("HotRouter: registered shard '%s'", name)

    def add(self, atom: MemoryAtom, shard: str = "default") -> None:
        """Add an atom to a named shard."""
        if shard not in self._shards:
            raise KeyError(f"Shard '{shard}' not registered. Call add_shard() first.")
        self._shards[shard].add(atom)

    def search(
        self,
        query: list[float],
        k: int = 10,
        shards: list[str] | None = None,
    ) -> list[MemorySearchResult]:
        """Search across specified shards (or all) and return merged top-k."""
        targets = shards or list(self._shards.keys())
        all_results: list[MemorySearchResult] = []
        for name in targets:
            shard = self._shards.get(name)
            if shard:
                all_results.extend(shard.search(query, k=k))
        all_results.sort(key=lambda r: r.score, reverse=True)
        return all_results[:k]

    def total_size(self) -> dict[str, int]:
        return {name: shard.size() for name, shard in self._shards.items()}
