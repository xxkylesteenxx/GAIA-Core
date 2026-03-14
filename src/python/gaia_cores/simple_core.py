"""SimpleGaiaCore — a reusable concrete GaiaCore implementation.

Primary uses:
  - Unit and integration tests (avoids duplicating boilerplate in every test)
  - Demo scripts that need live cores without domain-specific logic
  - Base class for lightweight custom cores

Spec ref: PYTHON-ORCHESTRATION-SPEC §4 — full GaiaCore contract.
"""

from __future__ import annotations

from .base import GaiaCore
from .models import CoreState, GaiaMessage, HealthReport, HealthStatus, StateUpdate, utc_now_iso


class SimpleGaiaCore(GaiaCore):
    """A generic, self-contained GaiaCore implementation.

    State is stored in a flat dict keyed by:
      - ``"started_at"`` / ``"stopped_at"`` — ISO timestamps set by lifecycle hooks
      - ``"msg::<topic>"``   — payload of the most recent message on that topic
      - ``"state::<scope>"`` — values from the most recent StateUpdate for that scope
      - ``"last_sender"``    — sender of the most recent message
      - ``"last_state_source"`` — source of the most recent StateUpdate
      - ``"last_message_topic"`` — included in snapshot when at least one message received
    """

    def __init__(self, core_id: str, domain: str, summary: str = "") -> None:
        super().__init__(core_id=core_id, domain=domain)
        self._running = False
        self._summary = summary
        self._values: dict[str, object] = {}
        self._last_message_topic = ""

    # -- Lifecycle ---------------------------------------------------------

    async def start(self) -> None:
        self._running = True
        self._values["started_at"] = utc_now_iso()

    async def stop(self) -> None:
        self._running = False
        self._values["stopped_at"] = utc_now_iso()

    # -- Health ------------------------------------------------------------

    async def health_check(self) -> HealthReport:
        return HealthReport(
            core_id=self.core_id,
            status=HealthStatus.HEALTHY if self._running else HealthStatus.STOPPED,
            detail=self._summary,
        )

    # -- Messaging ---------------------------------------------------------

    async def handle_message(self, message: GaiaMessage) -> None:
        self._last_message_topic = message.topic
        self._values[f"msg::{message.topic}"] = message.payload
        self._values["last_sender"] = message.sender

    # -- State -------------------------------------------------------------

    async def ingest_state_update(self, update: StateUpdate) -> None:
        self._values[f"state::{update.scope}"] = dict(update.values)
        self._values["last_state_source"] = update.source
        if update.summary:
            self._summary = update.summary

    def snapshot_state(self) -> CoreState:
        values = dict(self._values)
        if self._last_message_topic:
            values["last_message_topic"] = self._last_message_topic
        return CoreState(
            core_id=self.core_id,
            domain=self.domain,
            summary=self._summary,
            values=values,
        )
