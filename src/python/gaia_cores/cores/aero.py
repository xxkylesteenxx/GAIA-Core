"""AERO — atmospheric and aerial state core."""

from __future__ import annotations
from ..base import GaiaCore
from ..models import CoreState, GaiaMessage, HealthReport, HealthStatus, StateUpdate


class AeroCore(GaiaCore):
    def __init__(self) -> None:
        super().__init__(core_id="AERO", domain="atmosphere")
        self._health = HealthStatus.STOPPED
        self._values: dict = {}

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

    async def ingest_state_update(self, update: StateUpdate) -> None:
        self._values[f"state::{update.scope}"] = update.values

    def snapshot_state(self) -> CoreState:
        return CoreState(core_id=self.core_id, domain=self.domain,
                         health=self._health, values=dict(self._values))

    async def startup(self) -> None: await self.start()
    async def shutdown(self) -> None: await self.stop()
    def health(self) -> HealthStatus: return self._health
    def snapshot(self) -> CoreState: return self.snapshot_state()
