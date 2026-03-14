"""Abstract GaiaCore interface — contract every core must implement.

Spec ref: PYTHON-ORCHESTRATION-SPEC §4
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .models import CoreState, GaiaMessage, HealthReport, StateUpdate


class GaiaCore(ABC):
    """Abstract base for all eight GAIA cores.

    Each core is identified by a (core_id, domain) pair.
    The registry calls start() / stop() for lifecycle management.

    Spec ref: PYTHON-ORCHESTRATION-SPEC §4
    """

    def __init__(self, core_id: str, domain: str) -> None:
        self.core_id = core_id
        self.domain  = domain

    # -- Identity ----------------------------------------------------------

    @property
    def protection_class(self) -> str:
        """'critical' or 'bounded'. Override in subclasses."""
        return "bounded"

    def describe(self) -> dict[str, Any]:
        """Return a plain-dict summary of this core's identity."""
        return {"core_id": self.core_id, "domain": self.domain}

    # -- Lifecycle ---------------------------------------------------------

    @abstractmethod
    async def start(self) -> None:
        """Initialise resources. Called by registry at boot."""

    @abstractmethod
    async def stop(self) -> None:
        """Release resources. Called by registry at teardown."""

    # -- Health ------------------------------------------------------------

    @abstractmethod
    async def health_check(self) -> HealthReport:
        """Return the current health report for this core."""

    # -- Messaging ---------------------------------------------------------

    @abstractmethod
    async def handle_message(self, message: GaiaMessage) -> None:
        """Process an inbound GaiaMessage."""

    # -- State -------------------------------------------------------------

    @abstractmethod
    async def ingest_state_update(self, update: StateUpdate) -> None:
        """Receive and apply a StateUpdate from another core or the propagator."""

    @abstractmethod
    def snapshot_state(self) -> CoreState:
        """Export current state as a CoreState record."""
