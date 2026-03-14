"""VITA — biological and life-system state core."""

from __future__ import annotations
from ..base import GaiaCore
from ..models import CoreMessage, HealthStatus, StateSnapshot


class VitaCore(GaiaCore):
    def __init__(self) -> None:
        self._health = HealthStatus.STOPPED
        self._state: dict = {}

    @property
    def name(self) -> str:
        return "VITA"

    async def startup(self) -> None:
        self._health = HealthStatus.OK

    async def shutdown(self) -> None:
        self._health = HealthStatus.STOPPED

    def health(self) -> HealthStatus:
        return self._health

    async def handle_message(self, msg: CoreMessage) -> None:
        self._state[msg.topic] = msg.payload

    def snapshot(self) -> StateSnapshot:
        return StateSnapshot(core_name=self.name, health=self._health, state=dict(self._state))

    async def ingest_update(self, update: StateSnapshot) -> None:
        self._state[f"update_from_{update.core_name}"] = update.state
