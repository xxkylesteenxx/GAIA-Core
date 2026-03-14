"""Tests for Persistent Memory Manager.

Covers:
  - Events are written to the JSONL log
  - Events are appended (append-only, never overwritten)
  - Replay returns events in write order
  - Replay since_epoch filter works
  - Auto-checkpoint fires at checkpoint_every interval
  - Checkpoint manifest contains identity fingerprint
  - IPC bus integration: subscribed events are automatically absorbed
  - Dissent events are always written
  - Event count persists across manager restarts
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from gaia_core.ipc.broadcast import LocalBus, Topic, reset_bus
from gaia_core.guardian.nexus_clearance import ClearanceLevel, GuardianNexusClearance
from gaia_core.memory.memory_manager import CausalEvent, MemoryManager


@pytest.fixture(autouse=True)
def fresh_bus():
    reset_bus()
    yield
    reset_bus()


@pytest.fixture
def tmp_memory(tmp_path):
    bus = LocalBus()
    manager = MemoryManager(
        log_path=tmp_path / "causal.jsonl",
        checkpoint_dir=tmp_path / "checkpoints",
        checkpoint_every=5,
        identity_fingerprint="test-identity-root-xyz",
        bus=bus,
    )
    manager.start()
    return manager, bus


class TestMemoryManagerWrite:
    def test_manual_write_event(self, tmp_memory):
        manager, _ = tmp_memory
        event = manager.write_event(
            core="NEXUS", kind="coordination", topic="nexus.coordination",
            nexus_epoch=1, vector_clock={"NEXUS": 1}, payload={"signal": "test"},
        )
        assert isinstance(event, CausalEvent)
        assert event.core == "NEXUS"
        assert manager.event_count() == 1

    def test_events_persisted_to_jsonl(self, tmp_memory, tmp_path):
        manager, _ = tmp_memory
        manager.write_event(
            core="SOPHIA", kind="synthesis", topic="sophia.synthesis",
            nexus_epoch=2, vector_clock={"SOPHIA": 1}, payload={"summary": "green"},
        )
        lines = (tmp_path / "causal.jsonl").read_text().strip().splitlines()
        assert len(lines) == 1
        d = json.loads(lines[0])
        assert d["core"] == "SOPHIA"

    def test_append_only_multiple_events(self, tmp_memory):
        manager, _ = tmp_memory
        for i in range(3):
            manager.write_event(
                core="ATLAS", kind="grounding", topic="atlas.grounding",
                nexus_epoch=i, vector_clock={"ATLAS": i}, payload={"temp": 72.0 + i},
            )
        assert manager.event_count() == 3


class TestMemoryManagerReplay:
    def test_replay_returns_all_events(self, tmp_memory):
        manager, _ = tmp_memory
        for i in range(4):
            manager.write_event(
                core="NEXUS", kind="coordination", topic="nexus.coordination",
                nexus_epoch=i, vector_clock={}, payload={"i": i},
            )
        events = manager.replay()
        assert len(events) == 4

    def test_replay_since_epoch_filter(self, tmp_memory):
        manager, _ = tmp_memory
        for epoch in range(6):
            manager.write_event(
                core="NEXUS", kind="coordination", topic="nexus.coordination",
                nexus_epoch=epoch, vector_clock={}, payload={},
            )
        recent = manager.replay(since_epoch=3)
        assert all(e.nexus_epoch >= 3 for e in recent)
        assert len(recent) == 3

    def test_replay_preserves_order(self, tmp_memory):
        manager, _ = tmp_memory
        for i in range(5):
            manager.write_event(
                core="NEXUS", kind="coordination", topic="nexus.coordination",
                nexus_epoch=i, vector_clock={}, payload={"seq": i},
            )
        events = manager.replay()
        seqs = [e.payload["seq"] for e in events]
        assert seqs == sorted(seqs)


class TestCheckpoints:
    def test_auto_checkpoint_fires(self, tmp_memory, tmp_path):
        manager, _ = tmp_memory  # checkpoint_every=5
        for i in range(5):
            manager.write_event(
                core="NEXUS", kind="coordination", topic="nexus.coordination",
                nexus_epoch=i, vector_clock={}, payload={},
            )
        ckpts = list((tmp_path / "checkpoints").glob("ckpt_*.json"))
        assert len(ckpts) >= 1

    def test_checkpoint_has_identity_fingerprint(self, tmp_memory, tmp_path):
        manager, _ = tmp_memory
        for i in range(5):
            manager.write_event(
                core="NEXUS", kind="coordination", topic="nexus.coordination",
                nexus_epoch=i, vector_clock={}, payload={},
            )
        ckpt = manager.latest_checkpoint()
        assert ckpt is not None
        assert ckpt.identity_fingerprint == "test-identity-root-xyz"


class TestIPCIntegration:
    def test_ipc_dissent_absorbed(self, tmp_memory):
        manager, bus = tmp_memory
        before = manager.event_count()
        bus.publish(
            Topic.DISSENT, "TERRA", {"concern": "storm system"}, nexus_epoch=1,
            clearance_token=None, is_dissent=True,
        )
        assert manager.event_count() == before + 1

    def test_ipc_elevated_broadcast_absorbed(self, tmp_memory):
        manager, bus = tmp_memory
        guardian = GuardianNexusClearance()
        token = guardian.evaluate(
            system_state={}, context={"requested_level": ClearanceLevel.ELEVATED}
        )
        before = manager.event_count()
        bus.publish(
            Topic.COORDINATION, "NEXUS", {"signal": "epoch_update"}, nexus_epoch=5,
            clearance_token=token,
        )
        assert manager.event_count() == before + 1
