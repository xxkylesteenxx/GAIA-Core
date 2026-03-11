"""Tests for causal visibility gating in GAIA memory stack."""
from __future__ import annotations

import pytest

from gaia_core.memory.hlc import HybridLogicalClock, HLCTimestamp
from gaia_core.memory.metadata.session_frontier import SessionFrontier
from gaia_core.memory.retrieval.visibility_filter import VisibilityFilter
from gaia_core.memory.contracts import MemoryAtom, MemorySearchResult


def make_result(atom_id: str, timestamp_ns: int, score: float = 1.0) -> MemorySearchResult:
    atom = MemoryAtom(content="test", core="NEXUS", atom_id=atom_id, timestamp_ns=timestamp_ns)
    return MemorySearchResult(atom=atom, score=score, tier="hot")


def test_atom_visible_after_frontier_advance():
    frontier = SessionFrontier()
    vf = VisibilityFilter(frontier)
    session = "sess-001"

    hlc = HybridLogicalClock(node_id="nexus-01")
    ts = hlc.now()
    frontier.record_read(session, ts)

    result = make_result("atom-1", timestamp_ns=ts.wall_ns - 1000)
    filtered = vf.apply([result], session_id=session)
    assert filtered[0].visible is True


def test_atom_hidden_before_frontier():
    frontier = SessionFrontier()
    vf = VisibilityFilter(frontier)
    session = "sess-002"

    # Set frontier to now
    hlc = HybridLogicalClock(node_id="nexus-01")
    ts = hlc.now()
    frontier.record_read(session, ts)

    # Atom in the future
    future_ns = ts.wall_ns + 10_000_000_000  # 10 seconds ahead
    result = make_result("atom-future", timestamp_ns=future_ns)
    filtered = vf.apply([result], session_id=session)
    assert filtered[0].visible is False


def test_read_your_writes():
    frontier = SessionFrontier()
    vf = VisibilityFilter(frontier)
    session = "sess-003"

    hlc = HybridLogicalClock(node_id="nexus-01")
    ts = hlc.now()

    # Record write but do not advance read frontier
    frontier.record_write(session, "atom-mine", ts)

    future_ns = ts.wall_ns + 10_000_000_000
    result = make_result("atom-mine", timestamp_ns=future_ns)
    filtered = vf.apply([result], session_id=session)
    # Should be visible because session wrote it
    assert filtered[0].visible is True
