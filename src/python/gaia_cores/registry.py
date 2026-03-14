"""CoreRegistry — bootstraps, supervises, and snapshots all eight GAIA cores.

Spec ref: PYTHON-ORCHESTRATION-SPEC §6

Boot order: GUARDIAN is started before all other cores to ensure
the safety monitor is live before any policy-dependent core sends
or receives messages.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .models import HealthStatus, StateSnapshot

if TYPE_CHECKING:
    from .base import GaiaCore

log = logging.getLogger(__name__)

# GUARDIAN must boot first; remaining order is alphabetical.
_BOOT_ORDER = ["GUARDIAN", "SOPHIA", "NEXUS", "TERRA", "AQUA", "AERO", "VITA", "ETA"]


class CoreRegistry:
    """Manages lifecycle, health, and state for all GAIA cores."""

    def __init__(self) -> None:
        self._cores: dict[str, "GaiaCore"] = {}

    def register(self, core: "GaiaCore") -> None:
        self._cores[core.name] = core
        log.debug("registry: registered %s", core.name)

    async def boot(self) -> None:
        """Start all cores in policy-safe order."""
        ordered = sorted(
            self._cores.values(),
            key=lambda c: _BOOT_ORDER.index(c.name) if c.name in _BOOT_ORDER else 99,
        )
        for core in ordered:
            log.info("registry: starting %s [%s]", core.name, core.protection_class)
            await core.startup()

    async def shutdown(self) -> None:
        """Shut down all cores in reverse boot order."""
        ordered = sorted(
            self._cores.values(),
            key=lambda c: _BOOT_ORDER.index(c.name) if c.name in _BOOT_ORDER else 99,
            reverse=True,
        )
        for core in ordered:
            log.info("registry: stopping %s", core.name)
            await core.shutdown()

    def health_table(self) -> dict[str, HealthStatus]:
        """Return health status for every registered core."""
        return {name: core.health() for name, core in self._cores.items()}

    def snapshot_all(self) -> list[StateSnapshot]:
        """Return a state snapshot from every registered core."""
        return [core.snapshot() for core in self._cores.values()]

    def get(self, name: str) -> "GaiaCore | None":
        return self._cores.get(name)
