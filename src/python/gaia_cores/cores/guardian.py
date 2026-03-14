"""GUARDIAN — safety monitor; inspect-only, deny-by-default.

Spec ref: PYTHON-ORCHESTRATION-SPEC §8
protection_class: critical

GUARDIAN observes all messages and state transitions.
It does NOT mutate other cores' state directly.
Alerts are emitted as structured log entries.
"""

from __future__ import annotations
import logging
from ..base import GaiaCore
from ..models import CoreMessage, HealthStatus, StateSnapshot

log = logging.getLogger(__name__)


class GuardianCore(GaiaCore):
    def __init__(self) -> None:
        self._health = HealthStatus.STOPPED
        self._state: dict = {}
        self._alerts: list[dict] = []

    @property
    def name(self) -> str:
        return "GUARDIAN"

    @property
    def protection_class(self) -> str:
        return "critical"

    async def startup(self) -> None:
        self._health = HealthStatus.HEALTHY
        log.info("GUARDIAN: safety monitor online")

    async def shutdown(self) -> None:
        self._health = HealthStatus.STOPPED

    def health(self) -> HealthStatus:
        return self._health

    async def handle_message(self, msg: CoreMessage) -> None:
        """Inspect and store; alert on unexpected critical labels."""
        log.debug("GUARDIAN: inspecting [%s] %s -> %s",
                  msg.topic, msg.sender, msg.recipient or "*")
        # Store under "msg::<topic>" for snapshot assertions
        self._state[f"msg::{msg.topic}"] = msg.payload

        if msg.trust_label == "critical" and msg.sender not in ("SOPHIA", "GUARDIAN", "NEXUS"):
            alert = {"type": "unexpected_critical_label",
                     "sender": msg.sender, "topic": msg.topic}
            self._alerts.append(alert)
            log.warning("GUARDIAN: alert %s", alert)

    def snapshot(self) -> StateSnapshot:
        return StateSnapshot(
            core_name=self.name,
            health=self._health,
            state={**self._state, "alerts": list(self._alerts)},
        )

    async def ingest_update(self, update: StateSnapshot) -> None:
        log.debug("GUARDIAN: ingested update from %s", update.core_name)

    async def ingest_state_update(self, scope: str, values: dict) -> None:
        self._state[f"state::{scope}"] = values
