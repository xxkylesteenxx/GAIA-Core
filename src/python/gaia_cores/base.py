"""Abstract GaiaCore interface — contract every core must implement.

Spec ref: PYTHON-ORCHESTRATION-SPEC §4
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import CoreMessage, HealthStatus, StateSnapshot


class GaiaCore(ABC):
    """Abstract base for all eight GAIA cores.

    Subclasses must implement every abstract method.
    The registry calls startup() / shutdown() for lifecycle management.
    """

    # -- Identity ----------------------------------------------------------

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique core identifier (e.g. 'TERRA')."""

    @property
    def protection_class(self) -> str:
        """'critical' or 'bounded'. Override in subclasses."""
        return "bounded"

    # -- Lifecycle ---------------------------------------------------------

    @abstractmethod
    async def startup(self) -> None:
        """Initialise resources. Called by registry at boot."""

    @abstractmethod
    async def shutdown(self) -> None:
        """Release resources. Called by registry at teardown."""

    # -- Health ------------------------------------------------------------

    @abstractmethod
    def health(self) -> HealthStatus:
        """Return current health status."""

    # -- Messaging ---------------------------------------------------------

    @abstractmethod
    async def handle_message(self, msg: CoreMessage) -> None:
        """Process an inbound CoreMessage."""

    # -- State -------------------------------------------------------------

    @abstractmethod
    def snapshot(self) -> StateSnapshot:
        """Export current state as a serialisable record."""

    @abstractmethod
    async def ingest_update(self, update: StateSnapshot) -> None:
        """Receive and apply a state update from another core."""
