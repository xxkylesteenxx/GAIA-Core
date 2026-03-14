"""ETA — temporal coordination and event sequencing core."""

from __future__ import annotations
import time
from ..base import GaiaCore
from ..models import CoreState, GaiaMessage, HealthReport, HealthStatus, StateUpdate


class EtaCore(GaiaCore):
    def __init__(self) -> None:
        super().__init__(core_id="ETA", domain="temporal")
        self._health = HealthStatus.STOPPED
        self._values: dict = {}
        self._events: list[dict] = []

    @property
    def name(self) -> str:
        return self.core_id

    async def start(self) -> None:
        self._health = HealthStatus.HEALTHY

    async def stop(self) -> None:
        self._health = HealthStatus.STOPPED

    async def health_check(self) -> HealthReport:
        return HealthReport(core_id=self.core_id, domain=self.domain, status=self._health)

    async def handle_message(self, message: GaiaMessage) -> None:
        self._values[f"msg::{message.topic}"] = message.payload
        self._events.append({"topic": message.topic, "t": time.time()})

    async def ingest_state_update(self, update: StateUpdate) -> None:
        self._values[f"state::{update.scope}"] = update.values

    def snapshot_state(self) -> CoreState:
        return CoreState(
            core_id=self.core_id, domain=self.domain, health=self._health,
            values={**self._values, "event_count": len(self._events)},
        )

    async def startup(self) -> None: await self.start()
    async def shutdown(self) -> None: await self.stop()
    def health(self) -> HealthStatus: return self._health
    def snapshot(self) -> CoreState: return self.snapshot_state()
