"""Tier-aware federated retrieval router.

Searches hot tier first, falls back to capacity tier if:
  - hot tier returns fewer than min_results, or
  - caller requests capacity_fallback=True

Merges and deduplicates results by atom_id before returning.
"""
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from gaia_core.memory.contracts import MemorySearchResult
from gaia_core.memory.hot_index.faiss_hnsw_service import FaissHnswService
from gaia_core.memory.capacity_index.diskann_service import DiskANNService
from gaia_core.memory.retrieval.visibility_filter import VisibilityFilter

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)


class FederatedSearch:
    """Tier-aware federated search across hot and capacity tiers."""

    def __init__(
        self,
        hot: FaissHnswService,
        capacity: DiskANNService,
        visibility: VisibilityFilter,
        min_hot_results: int = 3,
    ) -> None:
        self._hot = hot
        self._capacity = capacity
        self._visibility = visibility
        self._min_hot = min_hot_results

    def search(
        self,
        query: list[float],
        k: int = 10,
        session_id: str = "",
        capacity_fallback: bool = False,
    ) -> list[MemorySearchResult]:
        """Search memory tiers and return causally visible top-k results."""
        t0 = time.monotonic()
        seen: dict[str, MemorySearchResult] = {}

        # Hot tier
        hot_results = self._hot.search(query, k=k)
        for r in hot_results:
            seen[r.atom.atom_id] = r

        # Capacity fallback
        if capacity_fallback or len(hot_results) < self._min_hot:
            log.debug("FederatedSearch: falling back to capacity tier")
            cap_results = self._capacity.search(query, k=k)
            for r in cap_results:
                if r.atom.atom_id not in seen:
                    seen[r.atom.atom_id] = r

        merged = sorted(seen.values(), key=lambda r: r.score, reverse=True)[:k]

        # Apply causal visibility
        if session_id:
            merged = self._visibility.apply(merged, session_id=session_id)

        total_ms = (time.monotonic() - t0) * 1000
        log.debug(
            "FederatedSearch: returned %d results in %.1f ms (session=%s)",
            len(merged), total_ms, session_id or "none",
        )
        return merged
