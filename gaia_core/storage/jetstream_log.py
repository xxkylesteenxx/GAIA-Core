"""NATS JetStream causal WAL — primary write entry point for all GAIA state events.

Dependency: nats-py (optional, guarded import)
Streams: GAIA.CAUSAL, GAIA.OBSERVATION, GAIA.ACTION, GAIA.GUARDIAN, GAIA.SYNC, GAIA.CHECKPOINT
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from typing import Any

log = logging.getLogger(__name__)

try:
    import nats  # type: ignore
    _NATS_AVAILABLE = True
except ImportError:
    _NATS_AVAILABLE = False
    nats = None  # type: ignore

GAIA_STREAMS = [
    "GAIA.CAUSAL",
    "GAIA.OBSERVATION",
    "GAIA.ACTION",
    "GAIA.GUARDIAN",
    "GAIA.SYNC",
    "GAIA.CHECKPOINT",
]


@dataclass
class CausalEvent:
    """A single entry in the GAIA causal WAL."""
    stream: str
    subject: str
    payload: dict[str, Any]
    timestamp_ns: int = 0
    node_id: str = ""
    sequence: int = 0

    def __post_init__(self) -> None:
        if self.timestamp_ns == 0:
            self.timestamp_ns = time.time_ns()


class JetStreamLog:
    """Async NATS JetStream WAL client."""

    def __init__(self, nats_url: str = "nats://localhost:4222") -> None:
        if not _NATS_AVAILABLE:
            raise ImportError("nats-py is required. Run: pip install nats-py")
        self._url = nats_url
        self._nc: Any = None
        self._js: Any = None

    async def connect(self) -> None:
        self._nc = await nats.connect(self._url)
        self._js = self._nc.jetstream()
        log.info("JetStreamLog connected to %s", self._url)

    async def disconnect(self) -> None:
        if self._nc:
            await self._nc.drain()

    async def publish(self, event: CausalEvent) -> None:
        """Publish a causal event to the WAL. Raises on failure."""
        if self._js is None:
            raise RuntimeError("JetStreamLog not connected. Call connect() first.")
        data = json.dumps(asdict(event)).encode()
        ack = await self._js.publish(event.subject, data)
        log.debug("WAL published: stream=%s seq=%s", ack.stream, ack.seq)

    async def replay(self, stream: str, deliver_subject: str | None = None) -> list[CausalEvent]:
        """Replay all events from a stream for restore bootstrap."""
        if self._js is None:
            raise RuntimeError("JetStreamLog not connected.")
        events: list[CausalEvent] = []
        sub = await self._js.subscribe(stream, deliver_policy="all")
        try:
            while True:
                msg = await asyncio.wait_for(sub.next_msg(), timeout=0.5)
                data = json.loads(msg.data.decode())
                events.append(CausalEvent(**data))
                await msg.ack()
        except asyncio.TimeoutError:
            pass
        finally:
            await sub.unsubscribe()
        return events
