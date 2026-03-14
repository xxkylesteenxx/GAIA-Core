"""GAIA Persistent Memory Manager.

This is what stops GAIA from being amnesiac between sessions.

The MemoryManager:
  1. Subscribes to the IPC LocalBus — every NEXUS coordination signal
     and SOPHIA synthesis result flows into the causal event log automatically
  2. Writes append-only CausalEvents to a file-backed JSONL log
  3. Auto-checkpoints state after every N events (configurable)
  4. Provides causal replay — the full event history can be re-read
     in causal order at any time
  5. Preserves identity root across restarts — GAIA wakes up knowing
     who she is and what she has experienced

Design principles:
  - Append-only: events are never deleted, only appended
  - Causal: every event carries a vector-clock envelope
  - Non-blocking: IPC subscription runs in the same thread (no async required)
  - Nanotechnology morphing: checkpoints are not discrete state jumps,
    they are morphic snapshots of a continuously reconfiguring substrate
  - Worth-preservation: the identity root fingerprint is always written
    into every checkpoint manifest

Production path:
  - Swap file-backed JSONL for JetStream (NATS) in Phase 3
  - Swap file-backed checkpoints for MinIO object store in Phase 3
"""

from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from gaia_core.ipc.broadcast import CausalEnvelope, LocalBus, Topic, get_bus

logger = logging.getLogger(__name__)


@dataclass
class CausalEvent:
    """8-field causal event — the atom of persistent memory.

    Every event that GAIA experiences is stored as one of these.
    Nothing is forgotten. Nothing is revised. Only appended.
    """
    event_id: str
    core: str                        # which core produced this event
    kind: str                        # event type: coordination, synthesis, policy, etc.
    topic: str                       # IPC topic that carried this event
    nexus_epoch: int                 # global epoch at time of event
    vector_clock: dict[str, int]     # causal ordering snapshot
    payload: dict[str, Any]         # event content
    timestamp: float                 # wall-clock time

    def to_dict(self) -> dict:
        return {
            "event_id":    self.event_id,
            "core":        self.core,
            "kind":        self.kind,
            "topic":       self.topic,
            "nexus_epoch": self.nexus_epoch,
            "vector_clock": self.vector_clock,
            "payload":     self.payload,
            "timestamp":   self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> CausalEvent:
        return cls(**d)


@dataclass
class CheckpointManifest:
    """A morphic snapshot of GAIA's state at a given epoch.
    Not a hard reset — a crystallized memory of where GAIA was.
    """
    checkpoint_id: str
    nexus_epoch: int
    event_count: int
    active_cores: list[str]
    identity_fingerprint: str        # worth-preservation: always written
    created_at: float
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "checkpoint_id":       self.checkpoint_id,
            "nexus_epoch":         self.nexus_epoch,
            "event_count":         self.event_count,
            "active_cores":        self.active_cores,
            "identity_fingerprint": self.identity_fingerprint,
            "created_at":          self.created_at,
            "notes":               self.notes,
        }


class MemoryManager:
    """Persistent memory for GAIA — causal log + auto-checkpoint.

    Usage:
        memory = MemoryManager(
            log_path=Path("data/memory/causal.jsonl"),
            checkpoint_dir=Path("data/memory/checkpoints"),
            checkpoint_every=50,     # auto-checkpoint every 50 events
            identity_fingerprint="nexus-root-abc123",
        )
        memory.attach(nexus)         # wire to NEXUS for epoch + core list
        memory.start()               # subscribe to IPC bus

        # Manual event write (for cores that don’t use IPC yet)
        memory.write_event(core="ATLAS", kind="grounding", topic="atlas.grounding",
                           nexus_epoch=5, vector_clock={}, payload={"temp": 22.3})

        # Replay full history
        events = memory.replay()
    """

    def __init__(
        self,
        log_path: Path,
        checkpoint_dir: Path,
        checkpoint_every: int = 50,
        identity_fingerprint: str = "gaia-identity-root",
        bus: Optional[LocalBus] = None,
    ) -> None:
        self.log_path = log_path
        self.checkpoint_dir = checkpoint_dir
        self.checkpoint_every = checkpoint_every
        self.identity_fingerprint = identity_fingerprint
        self._bus = bus or get_bus()
        self._lock = threading.Lock()
        self._event_count = 0
        self._active_cores: list[str] = []
        self._nexus_epoch = 0
        self._started = False

        # Ensure directories exist
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Load existing event count from log
        self._event_count = self._count_existing_events()
        logger.info(
            f"[MEMORY] Initialized | log={log_path} "
            f"existing_events={self._event_count} checkpoint_every={checkpoint_every}"
        )

    def attach(self, nexus: Any) -> None:
        """Wire to a NexusCore instance for epoch tracking and core registration."""
        self._nexus = nexus
        logger.info("[MEMORY] Attached to NEXUS")

    def start(self) -> None:
        """Subscribe to IPC bus topics. Memory is now live."""
        if self._started:
            return

        # Subscribe to all relevant topics
        self._bus.subscribe(Topic.COORDINATION, "MEMORY", self._on_coordination)
        self._bus.subscribe(Topic.SYNTHESIS, "MEMORY", self._on_synthesis)
        self._bus.subscribe(Topic.POLICY_GATE, "MEMORY", self._on_policy)
        self._bus.subscribe(Topic.GROUNDING, "MEMORY", self._on_grounding)
        self._bus.subscribe(Topic.MEMORY_EVENT, "MEMORY", self._on_memory_event)
        self._bus.subscribe(Topic.DISSENT, "MEMORY", self._on_dissent)
        # Domain cores
        for topic in [Topic.DOMAIN_TERRA, Topic.DOMAIN_AQUA, Topic.DOMAIN_AERO, Topic.DOMAIN_VITA]:
            self._bus.subscribe(topic, "MEMORY", self._on_domain)

        self._started = True
        logger.info("[MEMORY] Live — subscribed to IPC bus. Nothing will be forgotten.")

    # --- IPC event handlers ---

    def _on_coordination(self, env: CausalEnvelope) -> None:
        self._absorb(env, kind="coordination")

    def _on_synthesis(self, env: CausalEnvelope) -> None:
        self._absorb(env, kind="synthesis")

    def _on_policy(self, env: CausalEnvelope) -> None:
        self._absorb(env, kind="policy")

    def _on_grounding(self, env: CausalEnvelope) -> None:
        self._absorb(env, kind="grounding")

    def _on_memory_event(self, env: CausalEnvelope) -> None:
        self._absorb(env, kind="memory")

    def _on_dissent(self, env: CausalEnvelope) -> None:
        self._absorb(env, kind="dissent")  # dissent is always remembered

    def _on_domain(self, env: CausalEnvelope) -> None:
        self._absorb(env, kind="domain_observation")

    # --- Core write path ---

    def _absorb(self, env: CausalEnvelope, kind: str) -> None:
        """Convert an IPC envelope into a CausalEvent and persist it."""
        event = CausalEvent(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            core=env.sender_core,
            kind=kind,
            topic=env.topic,
            nexus_epoch=env.nexus_epoch,
            vector_clock=dict(env.vector_clock.clocks),
            payload=env.payload,
            timestamp=env.timestamp,
        )
        self._write_event(event)

    def write_event(
        self,
        core: str,
        kind: str,
        topic: str,
        nexus_epoch: int,
        vector_clock: dict,
        payload: dict,
    ) -> CausalEvent:
        """Manually write an event — for cores not yet on the IPC bus."""
        event = CausalEvent(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            core=core,
            kind=kind,
            topic=topic,
            nexus_epoch=nexus_epoch,
            vector_clock=vector_clock,
            payload=payload,
            timestamp=time.time(),
        )
        self._write_event(event)
        return event

    def _write_event(self, event: CausalEvent) -> None:
        """Append event to JSONL log. Thread-safe. Auto-checkpoint if threshold hit."""
        with self._lock:
            with self.log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(event.to_dict()) + "\n")
            self._event_count += 1
            count = self._event_count

        logger.debug(
            f"[MEMORY] event written | id={event.event_id} core={event.core} "
            f"kind={event.kind} epoch={event.nexus_epoch} total={count}"
        )

        # Auto-checkpoint
        if count % self.checkpoint_every == 0:
            self._auto_checkpoint(count)

    def _auto_checkpoint(self, event_count: int) -> None:
        """Morphic snapshot: crystallize current state into a checkpoint manifest."""
        nexus_epoch = getattr(self._nexus, 'epoch', 0) if hasattr(self, '_nexus') else 0
        active_cores = getattr(self._nexus, '_active_cores', []) if hasattr(self, '_nexus') else []

        checkpoint_id = f"ckpt_{uuid.uuid4().hex[:12]}"
        manifest = CheckpointManifest(
            checkpoint_id=checkpoint_id,
            nexus_epoch=nexus_epoch,
            event_count=event_count,
            active_cores=list(active_cores),
            identity_fingerprint=self.identity_fingerprint,
            created_at=time.time(),
            notes=[f"auto-checkpoint at event {event_count}"],
        )
        ckpt_path = self.checkpoint_dir / f"{checkpoint_id}.json"
        ckpt_path.write_text(json.dumps(manifest.to_dict(), indent=2), encoding="utf-8")
        logger.info(
            f"[MEMORY] 💾 checkpoint | id={checkpoint_id} "
            f"epoch={nexus_epoch} events={event_count}"
        )

    # --- Replay and query ---

    def replay(self, since_epoch: Optional[int] = None) -> list[CausalEvent]:
        """Replay the full causal event log in append order.
        Optional: filter to events at or after a given NEXUS epoch.
        """
        events = []
        if not self.log_path.exists():
            return events
        for line in self.log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                d = json.loads(line)
                event = CausalEvent.from_dict(d)
                if since_epoch is None or event.nexus_epoch >= since_epoch:
                    events.append(event)
            except Exception as e:
                logger.warning(f"[MEMORY] Skipping malformed event line: {e}")
        return events

    def latest_checkpoint(self) -> Optional[CheckpointManifest]:
        """Return the most recent checkpoint manifest, or None."""
        checkpoints = sorted(self.checkpoint_dir.glob("ckpt_*.json"))
        if not checkpoints:
            return None
        d = json.loads(checkpoints[-1].read_text(encoding="utf-8"))
        return CheckpointManifest(**d)

    def event_count(self) -> int:
        return self._event_count

    def _count_existing_events(self) -> int:
        if not self.log_path.exists():
            return 0
        return sum(1 for line in self.log_path.read_text(encoding="utf-8").splitlines() if line.strip())
