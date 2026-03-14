"""CoreRegistry — bootstraps, supervises, and snapshots all eight GAIA cores.

Spec ref: PYTHON-ORCHESTRATION-SPEC §6

Boot order: GUARDIAN is started before all other cores to ensure
the safety monitor is live before any policy-dependent core sends
or receives messages.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Iterable

from .models import CoreMessage, GaiaMessage, HealthReport, HealthStatus, StateSnapshot

if TYPE_CHECKING:
    from .base import GaiaCore

log = logging.getLogger(__name__)

# GUARDIAN must boot first; remaining order is deterministic.
_BOOT_ORDER = ["GUARDIAN", "SOPHIA", "NEXUS", "TERRA", "AQUA", "AERO", "VITA", "ETA"]


class CoreRegistry:
    """Manages lifecycle, health, and state for all GAIA cores."""

    def __init__(self) -> None:
        self._cores: dict[str, "GaiaCore"] = {}

    # -- Registration ------------------------------------------------------

    def register(self, core: "GaiaCore") -> None:
        self._cores[core.name] = core
        log.debug("registry: registered %s", core.name)

    async def register_many(self, cores: Iterable["GaiaCore"]) -> None:
        """Register multiple cores at once (async-compatible convenience method)."""
        for core in cores:
            self.register(core)

    # -- Lifecycle ---------------------------------------------------------

    def _ordered(self, reverse: bool = False) -> list["GaiaCore"]:
        return sorted(
            self._cores.values(),
            key=lambda c: _BOOT_ORDER.index(c.name) if c.name in _BOOT_ORDER else 99,
            reverse=reverse,
        )

    async def boot(self) -> None:
        """Start all cores in policy-safe order."""
        await self.boot_all()

    async def boot_all(self) -> None:
        """Start all cores in policy-safe order (GUARDIAN first)."""
        for core in self._ordered():
            log.info("registry: starting %s [%s]", core.name, core.protection_class)
            await core.startup()

    async def shutdown(self) -> None:
        """Shut down all cores in reverse boot order."""
        await self.stop_all()

    async def stop_all(self) -> None:
        """Shut down all cores in reverse boot order."""
        for core in self._ordered(reverse=True):
            log.info("registry: stopping %s", core.name)
            await core.shutdown()

    # -- Messaging ---------------------------------------------------------

    async def send(self, msg: GaiaMessage) -> None:
        """Deliver a GaiaMessage directly to its named recipient core.

        Bypasses bus route-table; intended for registry-level control messages.
        Use CoreMessageBus.dispatch() for policy-checked routing.
        """
        if msg.recipient is None:
            log.warning("registry.send: broadcast not supported; use StatePropagator")
            return
        core = self._cores.get(msg.recipient)
        if core is None:
            log.warning("registry.send: unknown recipient '%s'", msg.recipient)
            return
        await core.handle_message(msg)

    # -- Health & State ----------------------------------------------------

    async def health_table(self) -> dict[str, HealthReport]:
        """Return a HealthReport for every registered core."""
        return {
            name: HealthReport(core_name=name, status=core.health())
            for name, core in self._cores.items()
        }

    def snapshot_all(self) -> dict[str, StateSnapshot]:
        """Return a state snapshot from every registered core, keyed by name."""
        return {core.name: core.snapshot() for core in self._cores.values()}

    def get(self, name: str) -> "GaiaCore | None":
        return self._cores.get(name)
