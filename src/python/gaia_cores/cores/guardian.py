"""GUARDIAN — safety monitor; inspect-only, deny-by-default.

Spec ref: PYTHON-ORCHESTRATION-SPEC §8 · protection_class: critical
"""

from __future__ import annotations
import logging
from ..base import GaiaCore
from ..models import CoreState, GaiaMessage, HealthReport, HealthStatus, StateUpdate

log = logging.getLogger(__name__)


class GuardianCore(GaiaCore):
    def __init__(self) -> None:
        super().__init__(core_id="GUARDIAN", domain="safety")
        self._health = HealthStatus.STOPPED
        self._values: dict = {}
        self._alerts: list[dict] = []

    @property
    def name(self) -> str:
        return self.core_id

    @property
    def protection_class(self) -> str:
        return "critical"

    async def start(self) -> None:
        self._health = HealthStatus.HEALTHY
        log.info("GUARDIAN: safety monitor online")

    async def stop(self) -> None:
        self._health = HealthStatus.STOPPED

    async def health_check(self) -> HealthReport:
        return HealthReport(core_id=self.core_id, domain=self.domain, status=self._health)

    async def handle_message(self, message: GaiaMessage) -> None:
        log.debug("GUARDIAN: inspecting [%s] %s -> %s",
                  message.topic, message.sender, message.recipient or "*")
        self._values[f"msg::{message.topic}"] = message.payload
        if (message.trust_label == "critical"
                and message.sender not in ("SOPHIA", "GUARDIAN", "NEXUS")):
            alert = {"type": "unexpected_critical_label",
                     "sender": message.sender, "topic": message.topic}
            self._alerts.append(alert)
            log.warning("GUARDIAN: alert %s", alert)

    async def ingest_state_update(self, update: StateUpdate) -> None:
        self._values[f"state::{update.scope}"] = update.values

    def snapshot_state(self) -> CoreState:
        return CoreState(
            core_id=self.core_id, domain=self.domain, health=self._health,
            values={**self._values, "alerts": list(self._alerts)},
        )

    async def startup(self) -> None: await self.start()
    async def shutdown(self) -> None: await self.stop()
    def health(self) -> HealthStatus: return self._health
    def snapshot(self) -> CoreState: return self.snapshot_state()
