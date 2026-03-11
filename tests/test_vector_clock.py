"""Tests for VectorClockService IPC layer."""
from __future__ import annotations

from gaia_core.ipc.causal.vector_clock import VectorClockService
from gaia_core.ipc.contracts import GaiaEnvelope, DataClass


def test_tick_increments_local():
    svc = VectorClockService(node_id="nexus-01")
    c1 = svc.tick()
    c2 = svc.tick()
    assert c2.versions["nexus-01"] == c1.versions["nexus-01"] + 1


def test_receive_merges_remote():
    svc = VectorClockService(node_id="nexus-01")
    svc.tick()  # local at 1
    remote = {"guardian-01": 5, "nexus-01": 0}
    merged = svc.receive(remote)
    assert merged.versions["guardian-01"] == 5
    assert merged.versions["nexus-01"] >= 1


def test_stamp_attaches_clock_to_envelope():
    svc = VectorClockService(node_id="nexus-01")
    env = GaiaEnvelope(source_core="NEXUS", target_core="GUARDIAN", data_class=DataClass.A)
    stamped = svc.stamp(env)
    assert "nexus-01" in stamped.causal_clock
    assert stamped.causal_clock["nexus-01"] >= 1


def test_happened_before():
    svc = VectorClockService(node_id="a")
    a1 = svc.tick().versions
    a2 = svc.tick().versions
    assert svc.happened_before(a1, a2)
    assert not svc.happened_before(a2, a1)


def test_concurrent_with():
    svc_a = VectorClockService(node_id="a")
    svc_b = VectorClockService(node_id="b")
    ca = svc_a.tick().versions
    cb = svc_b.tick().versions
    # Independent clocks are concurrent
    assert svc_a.concurrent_with(ca, cb)
