"""Tests for read-your-writes and monotonic read guarantees."""
from __future__ import annotations

from gaia_core.memory.hlc import HybridLogicalClock
from gaia_core.memory.metadata.session_frontier import SessionFrontier


def test_write_advances_read_frontier():
    """Recording a write should also advance the read frontier (read-your-writes)."""
    frontier = SessionFrontier()
    hlc = HybridLogicalClock(node_id="test-node")
    session = "sess-ryw-01"

    ts = hlc.now()
    frontier.record_write(session, "atom-a", ts)

    state = frontier.get_or_create(session)
    assert state.read_frontier is not None
    assert state.read_frontier == ts


def test_monotonic_read_never_goes_backwards():
    """Read frontier should never decrease."""
    frontier = SessionFrontier()
    hlc = HybridLogicalClock(node_id="test-node")
    session = "sess-mono-01"

    ts1 = hlc.now()
    ts2 = hlc.now()
    assert ts2 > ts1

    frontier.record_read(session, ts2)
    frontier.record_read(session, ts1)  # should not regress

    state = frontier.get_or_create(session)
    assert state.read_frontier == ts2


def test_write_tracked_in_session():
    frontier = SessionFrontier()
    hlc = HybridLogicalClock(node_id="test-node")
    session = "sess-track-01"

    ts = hlc.now()
    frontier.record_write(session, "atom-xyz", ts)

    state = frontier.get_or_create(session)
    assert "atom-xyz" in state.written_atom_ids
