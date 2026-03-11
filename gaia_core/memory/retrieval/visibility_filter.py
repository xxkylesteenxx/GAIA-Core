"""Causal visibility filter for memory retrieval.

Gates search results based on session causal frontier.
Results whose HLC timestamp is ahead of the session frontier
are hidden until the session advances.
"""
from __future__ import annotations

import logging

from gaia_core.memory.contracts import MemorySearchResult
from gaia_core.memory.hlc import HLCTimestamp
from gaia_core.memory.metadata.session_frontier import SessionFrontier

log = logging.getLogger(__name__)


class VisibilityFilter:
    """Applies session causal frontier to a list of MemorySearchResults."""

    def __init__(self, frontier: SessionFrontier) -> None:
        self._frontier = frontier

    def apply(
        self,
        results: list[MemorySearchResult],
        session_id: str,
    ) -> list[MemorySearchResult]:
        """Filter results to only those visible to the given session.

        Atoms that fail the visibility check are returned with visible=False
        rather than dropped, so callers can log/audit the gated results.
        """
        out: list[MemorySearchResult] = []
        for r in results:
            atom_hlc = HLCTimestamp(
                wall_ns=r.atom.timestamp_ns,
                logical=0,
                node_id=r.atom.core,
            )
            visible = self._frontier.is_visible(
                session_id=session_id,
                atom_hlc=atom_hlc,
                atom_id=r.atom.atom_id,
            )
            if not visible:
                log.debug(
                    "Gating atom %s from session %s (causal frontier)",
                    r.atom.atom_id, session_id,
                )
            out.append(MemorySearchResult(
                atom=r.atom,
                score=r.score,
                tier=r.tier,
                latency_ms=r.latency_ms,
                visible=visible,
            ))
        return out
