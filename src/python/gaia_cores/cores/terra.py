"""TERRA — environmental state and physical substrate core."""

from __future__ import annotations
from ..base import GaiaCore
from ..models import CoreMessage, HealthStatus, StateSnapshot


class TerraCore(GaiaCore):
    def __init__(self) -> None:
        self._health = HealthStatus.STOPPED
        self._state: dict = {}

    @property
    def name(self) -> str:
        return "TERRA"

    async def startup(self) -> None:
        self._health = HealthStatus.HEALTHY

    async def shutdown(self) -> None:
        self._health = HealthStatus.STOPPED

    def health(self) -> HealthStatus:
        return self._health

    async def handle_message(self, msg: CoreMessage) -> None:
        # Store under "msg::<topic>" so tests can assert by key
        self._state[f"msg::{msg.topic}"] = msg.payload

    def snapshot(self) -> StateSnapshot:
        return StateSnapshot(core_name=self.name, health=self._health, state=dict(self._state))

    async def ingest_update(self, update: StateSnapshot) -> None:
        self._state[f"update_from_{update.core_name}"] = update.state

    async def ingest_state_update(self, scope: str, values: dict) -> None:
        """Called by StatePropagator.selective to store scoped state."""
        self._state[f"state::{scope}"] = values
