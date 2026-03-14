"""CoreRegistry — bootstraps, supervises, and snapshots all eight GAIA cores.

Spec ref: PYTHON-ORCHESTRATION-SPEC §6

Boot order: GUARDIAN is started before all other cores.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Iterable

from .models import CoreState, GaiaMessage, HealthReport, HealthStatus

if TYPE_CHECKING:
    from .base import GaiaCore

log = logging.getLogger(__name__)

_BOOT_ORDER = ["GUARDIAN", "SOPHIA", "NEXUS", "TERRA", "AQUA", "AERO", "VITA", "ETA"]


class CoreRegistry:
    def __init__(self) -> None:
        self._cores: dict[str, "GaiaCore"] = {}

    # -- Registration ------------------------------------------------------

    def register(self, core: "GaiaCore") -> None:
        self._cores[core.core_id] = core
        log.debug("registry: registered %s", core.core_id)

    async def register_many(self, cores: Iterable["GaiaCore"]) -> None:
        for core in cores:
            self.register(core)

    # -- Lifecycle ---------------------------------------------------------

    def _ordered(self, reverse: bool = False) -> list["GaiaCore"]:
        return sorted(
            self._cores.values(),
            key=lambda c: _BOOT_ORDER.index(c.core_id) if c.core_id in _BOOT_ORDER else 99,
            reverse=reverse,
        )

    async def boot_all(self) -> None:
        for core in self._ordered():
            log.info("registry: starting %s [%s]", core.core_id, core.protection_class)
            await core.start()

    async def stop_all(self) -> None:
        for core in self._ordered(reverse=True):
            log.info("registry: stopping %s", core.core_id)
            await core.stop()

    # Backward-compat aliases
    async def boot(self) -> None: await self.boot_all()
    async def shutdown(self) -> None: await self.stop_all()

    # -- Messaging ---------------------------------------------------------

    async def send(self, msg: GaiaMessage) -> None:
        """Deliver a GaiaMessage directly to its named recipient core."""
        if msg.recipient is None:
            log.warning("registry.send: use StatePropagator for broadcast")
            return
        core = self._cores.get(msg.recipient)
        if core is None:
            log.warning("registry.send: unknown recipient '%s'", msg.recipient)
            return
        await core.handle_message(msg)

    # -- Health & State ----------------------------------------------------

    async def health_table(self) -> dict[str, HealthReport]:
        result = {}
        for name, core in self._cores.items():
            result[name] = await core.health_check()
        return result

    def snapshot_all(self) -> dict[str, CoreState]:
        return {core.core_id: core.snapshot_state() for core in self._cores.values()}

    def get(self, name: str) -> "GaiaCore | None":
        return self._cores.get(name)
