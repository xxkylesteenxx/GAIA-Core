"""Tests for causal broadcast holdback and delivery."""
from __future__ import annotations

from gaia_core.ipc.causal.causal_broadcast import CausalBroadcast
from gaia_core.ipc.contracts import GaiaEnvelope, DataClass


def _env(source: str, clock: dict) -> GaiaEnvelope:
    return GaiaEnvelope(
        source_core=source,
        target_core="*",
        data_class=DataClass.A,
        causal_clock=clock,
    )


def test_in_order_delivery():
    delivered = []
    cb = CausalBroadcast(node_id="nexus-01", on_deliver=delivered.append)

    m1 = _env("NEXUS", {"NEXUS": 1})
    m2 = _env("NEXUS", {"NEXUS": 2})

    cb.receive(m1)
    cb.receive(m2)

    assert len(delivered) == 2
    assert delivered[0].causal_clock["NEXUS"] == 1
    assert delivered[1].causal_clock["NEXUS"] == 2


def test_out_of_order_holdback_then_release():
    delivered = []
    cb = CausalBroadcast(node_id="nexus-01", on_deliver=delivered.append)

    m1 = _env("NEXUS", {"NEXUS": 1})
    m2 = _env("NEXUS", {"NEXUS": 2})

    # Deliver m2 first — should be held back
    cb.receive(m2)
    assert len(delivered) == 0
    assert cb.holdback_depth() == 1

    # Now deliver m1 — should release both
    cb.receive(m1)
    assert len(delivered) == 2
    assert cb.holdback_depth() == 0


def test_no_clock_message_always_delivered():
    delivered = []
    cb = CausalBroadcast(node_id="nexus-01", on_deliver=delivered.append)
    # Message with empty clock — should always deliver
    env = GaiaEnvelope(source_core="SOPHIA", target_core="NEXUS", causal_clock={})
    cb.receive(env)
    assert len(delivered) == 1
