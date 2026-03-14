"""NEXUS — routing, federation, and cross-system IPC coordinator.

Spec ref: PYTHON-ORCHESTRATION-SPEC §8
protection_class: critical

NEXUS coordinates routing but SHALL NOT bypass lower-layer isolation.
"""

from __future__ import annotations
import logging
from ..base import GaiaCore
from ..models import CoreMessage, HealthStatus, StateSnapshot

log = logging.getLogger(__name__)


class NexusCore(GaiaCore):
    def __init__(self) -> None:
        self._health = HealthStatus.STOPPED
        self._routes: list[dict] = []

    @property
    def name(self) -> str:
        return "NEXUS"

    @property
    def protection_class(self) -> str:
        return "critical"

    async def startup(self) -> None:
        self._health = HealthStatus.OK
        log.info("NEXUS: routing fabric online")

    async def shutdown(self) -> None:
        self._health = HealthStatus.STOPPED

    def health(self) -> HealthStatus:
        return self._health

    async def handle_message(self, msg: CoreMessage) -> None:
        log.debug("NEXUS: routing [%s] from %s", msg.topic, msg.sender)
        self._routes.append({"topic": msg.topic, "sender": msg.sender})

    def snapshot(self) -> StateSnapshot:
        return StateSnapshot(
            core_name=self.name,
            health=self._health,
            state={"routes_seen": len(self._routes)},
        )

    async def ingest_update(self, update: StateSnapshot) -> None:
        pass
