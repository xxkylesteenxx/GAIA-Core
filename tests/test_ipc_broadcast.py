"""Tests for IPC Causal Broadcast Fabric — ADR-008.

Covers:
  - Vector clock ticks on each publish
  - Causal ordering: happened_before is correctly detected
  - Vector clock merge takes element-wise max
  - Subscriber receives envelope
  - DISSENT topic bypasses clearance gate and is always delivered
  - ELEVATED clearance required for non-dissent broadcast
  - Message log captures all envelopes including blocked ones
  - Bus reset works for test isolation
  - 11 canonical topics exist
"""

from __future__ import annotations

import pytest

from gaia_core.ipc.broadcast import (
    LocalBus,
    Topic,
    VectorClock,
    CausalEnvelope,
    get_bus,
    reset_bus,
)
from gaia_core.guardian.nexus_clearance import ClearanceLevel, GuardianNexusClearance


@pytest.fixture(autouse=True)
def fresh_bus():
    reset_bus()
    yield
    reset_bus()


class TestVectorClock:
    def test_tick_increments_core_slot(self):
        vc = VectorClock()
        vc2 = vc.tick("NEXUS")
        assert vc2.clocks["NEXUS"] == 1

    def test_tick_does_not_mutate_original(self):
        vc = VectorClock()
        vc2 = vc.tick("NEXUS")
        assert "NEXUS" not in vc.clocks

    def test_merge_takes_max(self):
        a = VectorClock(clocks={"NEXUS": 3, "SOPHIA": 1})
        b = VectorClock(clocks={"NEXUS": 1, "SOPHIA": 5})
        merged = a.merge(b)
        assert merged.clocks["NEXUS"] == 3
        assert merged.clocks["SOPHIA"] == 5

    def test_happened_before(self):
        a = VectorClock(clocks={"NEXUS": 1})
        b = VectorClock(clocks={"NEXUS": 2})
        assert a.happened_before(b)
        assert not b.happened_before(a)

    def test_concurrent_clocks_not_causally_ordered(self):
        a = VectorClock(clocks={"NEXUS": 2, "SOPHIA": 1})
        b = VectorClock(clocks={"NEXUS": 1, "SOPHIA": 2})
        assert not a.happened_before(b)
        assert not b.happened_before(a)


class TestLocalBus:
    def _elevated_token(self):
        guardian = GuardianNexusClearance()
        return guardian.evaluate(
            system_state={}, context={"requested_level": ClearanceLevel.ELEVATED}
        )

    def test_subscriber_receives_envelope(self):
        bus = LocalBus()
        received = []
        bus.subscribe(Topic.COORDINATION, "SOPHIA", received.append)
        token = self._elevated_token()
        bus.publish(Topic.COORDINATION, "NEXUS", {"signal": "test"}, nexus_epoch=1,
                    clearance_token=token)
        assert len(received) == 1
        assert received[0].sender_core == "NEXUS"
        assert received[0].topic == Topic.COORDINATION

    def test_dissent_always_delivered_without_clearance(self):
        bus = LocalBus()
        received = []
        bus.subscribe(Topic.DISSENT, "MEMORY", received.append)
        # No clearance token — dissent must still be delivered
        bus.publish(Topic.DISSENT, "TERRA", {"concern": "anomaly"}, nexus_epoch=1,
                    clearance_token=None, is_dissent=True)
        assert len(received) == 1

    def test_no_clearance_blocks_non_dissent(self):
        bus = LocalBus()
        received = []
        bus.subscribe(Topic.SYNTHESIS, "MEMORY", received.append)
        bus.publish(Topic.SYNTHESIS, "SOPHIA", {"result": "x"}, nexus_epoch=1,
                    clearance_token=None)  # no clearance
        assert len(received) == 0  # blocked, not delivered

    def test_blocked_message_still_in_log(self):
        bus = LocalBus()
        bus.publish(Topic.SYNTHESIS, "SOPHIA", {"result": "x"}, nexus_epoch=1,
                    clearance_token=None)
        log = bus.get_log()
        assert len(log) == 1  # logged even if not delivered

    def test_vector_clock_advances_per_publish(self):
        bus = LocalBus()
        token = self._elevated_token()
        bus.publish(Topic.COORDINATION, "NEXUS", {}, nexus_epoch=1, clearance_token=token)
        bus.publish(Topic.COORDINATION, "NEXUS", {}, nexus_epoch=2, clearance_token=token)
        vc = bus.get_vector_clock("NEXUS")
        assert vc.clocks["NEXUS"] == 2

    def test_eleven_canonical_topics(self):
        assert len(list(Topic)) == 11
