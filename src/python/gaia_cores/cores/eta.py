"""ETA — temporal coordination and event sequencing core."""

from __future__ import annotations
import time
from ..base import GaiaCore
from ..models import CoreMessage, HealthStatus, StateSnapshot


class EtaCore(GaiaCore):
    def __init__(self) -> None:
        self._health = HealthStatus.STOPPED
        self._state: dict = {}
        self._events: list[dict] = []

    @property
    def name(self) -> str:
        return "ETA"

    async def startup(self) -> None:
        self._health = HealthStatus.HEALTHY

    async def shutdown(self) -> None:
        self._health = HealthStatus.STOPPED

    def health(self) -> HealthStatus:
        return self._health

    async def handle_message(self, msg: CoreMessage) -> None:
        self._state[f"msg::{msg.topic}"] = msg.payload
        self._events.append({"topic": msg.topic, "t": time.time()})

    def snapshot(self) -> StateSnapshot:
        return StateSnapshot(
            core_name=self.name,
            health=self._health,
            state={**self._state, "event_count": len(self._events)},
        )

    async def ingest_update(self, update: StateSnapshot) -> None:
        pass

    async def ingest_state_update(self, scope: str, values: dict) -> None:
        self._state[f"state::{scope}"] = values
