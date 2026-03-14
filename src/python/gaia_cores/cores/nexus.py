"""NEXUS — routing, federation, and cross-system IPC coordinator.

Spec ref: PYTHON-ORCHESTRATION-SPEC §8
protection_class: critical
"""

from __future__ import annotations
import logging
from ..base import GaiaCore
from ..models import CoreMessage, HealthStatus, StateSnapshot

log = logging.getLogger(__name__)


class NexusCore(GaiaCore):
    def __init__(self) -> None:
        self._health = HealthStatus.STOPPED
        self._state: dict = {}
        self._routes: list[dict] = []

    @property
    def name(self) -> str:
        return "NEXUS"

    @property
    def protection_class(self) -> str:
        return "critical"

    async def startup(self) -> None:
        self._health = HealthStatus.HEALTHY
        log.info("NEXUS: routing fabric online")

    async def shutdown(self) -> None:
        self._health = HealthStatus.STOPPED

    def health(self) -> HealthStatus:
        return self._health

    async def handle_message(self, msg: CoreMessage) -> None:
        self._state[f"msg::{msg.topic}"] = msg.payload
        self._routes.append({"topic": msg.topic, "sender": msg.sender})

    def snapshot(self) -> StateSnapshot:
        return StateSnapshot(
            core_name=self.name,
            health=self._health,
            state={**self._state, "routes_seen": len(self._routes)},
        )

    async def ingest_update(self, update: StateSnapshot) -> None:
        pass

    async def ingest_state_update(self, scope: str, values: dict) -> None:
        self._state[f"state::{scope}"] = values
