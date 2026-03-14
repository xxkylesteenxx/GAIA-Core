"""CoreRegistry — bootstraps, supervises, and snapshots all eight GAIA cores.

Spec ref: PYTHON-ORCHESTRATION-SPEC §6

Boot order note: boot_all() uses TaskGroup for concurrent startup.
If GUARDIAN-first ordering is required, call start() manually in
_BOOT_ORDER sequence before calling boot_all() for the remainder,
or boot cores sequentially via: for cid in _BOOT_ORDER: await registry.get(cid).start()
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable

from .base import GaiaCore
from .bus import GaiaMessageBus
from .models import CoreState, GaiaMessage, HealthReport

log = logging.getLogger(__name__)

_BOOT_ORDER = ["GUARDIAN", "SOPHIA", "NEXUS", "TERRA", "AQUA", "AERO", "VITA", "ETA"]


class CoreRegistry:
    """Manages lifecycle, messaging, health, and state for all GAIA cores.

    An optional GaiaMessageBus may be injected; if omitted a private
    bus is created. All registered cores are automatically subscribed
    to the bus under their core_id route.
    """

    def __init__(self, bus: GaiaMessageBus | None = None) -> None:
        self.bus: GaiaMessageBus = bus or GaiaMessageBus()
        self._cores: dict[str, GaiaCore] = {}

    # -- Registration ------------------------------------------------------

    async def register(self, core: GaiaCore) -> None:
        """Register a core and subscribe it to the bus.

        Raises ValueError if a core with the same core_id is already registered.
        """
        if core.core_id in self._cores:
            raise ValueError(f"core already registered: {core.core_id}")
        self._cores[core.core_id] = core
        await self.bus.subscribe(core.core_id, core.handle_message)
        log.debug("registry: registered %s", core.core_id)

    async def register_many(self, cores: Iterable[GaiaCore]) -> None:
        """Register multiple cores in sequence."""
        for core in cores:
            await self.register(core)

    # -- Identity ----------------------------------------------------------

    @property
    def core_ids(self) -> tuple[str, ...]:
        """Registered core IDs in insertion order."""
        return tuple(self._cores.keys())

    def get(self, core_id: str) -> GaiaCore:
        """Return the core for core_id; raises KeyError if not registered."""
        return self._cores[core_id]

    # -- Lifecycle ---------------------------------------------------------

    async def boot_all(self) -> None:
        """Start all cores concurrently via TaskGroup.

        For strict GUARDIAN-first ordering, boot cores sequentially:
            for cid in ["GUARDIAN", ...]: await registry.get(cid).start()
        """
        async with asyncio.TaskGroup() as tg:
            for core in self._cores.values():
                tg.create_task(core.start(), name=f"start-{core.core_id}")

    async def stop_all(self) -> None:
        """Stop all cores concurrently via TaskGroup."""
        async with asyncio.TaskGroup() as tg:
            for core in self._cores.values():
                tg.create_task(core.stop(), name=f"stop-{core.core_id}")

    async def boot_ordered(self) -> None:
        """Start cores sequentially in GUARDIAN-first policy-safe order."""
        ordered = sorted(
            self._cores.values(),
            key=lambda c: _BOOT_ORDER.index(c.core_id) if c.core_id in _BOOT_ORDER else 99,
        )
        for core in ordered:
            log.info("registry: starting %s [%s]", core.core_id, core.protection_class)
            await core.start()

    async def stop_ordered(self) -> None:
        """Stop cores sequentially in reverse boot order."""
        ordered = sorted(
            self._cores.values(),
            key=lambda c: _BOOT_ORDER.index(c.core_id) if c.core_id in _BOOT_ORDER else 99,
            reverse=True,
        )
        for core in ordered:
            log.info("registry: stopping %s", core.core_id)
            await core.stop()

    # Backward-compat aliases
    async def boot(self) -> None: await self.boot_ordered()
    async def shutdown(self) -> None: await self.stop_ordered()

    # -- Messaging ---------------------------------------------------------

    async def send(self, message: GaiaMessage) -> None:
        """Publish message to the bus (routes to recipient or broadcasts)."""
        await self.bus.publish(message)

    # -- Health & State ----------------------------------------------------

    async def health_table(self) -> dict[str, HealthReport]:
        """Concurrently collect health reports from all cores."""
        reports = await asyncio.gather(
            *(core.health_check() for core in self._cores.values())
        )
        return {report.core_id: report for report in reports}

    def snapshot_all(self) -> dict[str, CoreState]:
        """Return a CoreState snapshot from every registered core."""
        return {core_id: core.snapshot_state()
                for core_id, core in self._cores.items()}
