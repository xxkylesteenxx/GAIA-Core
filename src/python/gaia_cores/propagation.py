"""Planetary state propagation.

Spec ref: PYTHON-ORCHESTRATION-SPEC §7

Uses asyncio.TaskGroup (Python 3.11+) for concurrent delivery with
structured cancellation: if any ingest_state_update raises, all
sibling tasks are cancelled and the exception propagates cleanly.
"""

from __future__ import annotations

import asyncio
import logging

from .models import StateUpdate
from .registry import CoreRegistry

log = logging.getLogger(__name__)


class StatePropagator:
    def __init__(self, registry: CoreRegistry) -> None:
        self.registry = registry

    async def broadcast(self, update: StateUpdate) -> None:
        """Deliver update concurrently to every registered core.

        Spec ref: PYTHON-ORCHESTRATION-SPEC §7 — full broadcast.
        """
        async with asyncio.TaskGroup() as tg:
            for core_id in self.registry.core_ids:
                core = self.registry.get(core_id)
                if core is not None:
                    tg.create_task(
                        core.ingest_state_update(update),
                        name=f"propagate-{core_id}",
                    )
        log.debug("propagation: broadcast scope='%s' from '%s'",
                  update.scope, update.source)

    async def selective(
        self,
        update: StateUpdate,
        targets: list[str],
    ) -> None:
        """Deliver update concurrently to named target cores only.

        Spec ref: PYTHON-ORCHESTRATION-SPEC §7 — selective delivery.
        Unknown targets are logged and skipped; they do not abort delivery
        to the remaining targets.
        """
        valid = []
        for core_id in targets:
            core = self.registry.get(core_id)
            if core is None:
                log.warning("propagation: unknown target '%s'", core_id)
            else:
                valid.append((core_id, core))

        if not valid:
            return

        async with asyncio.TaskGroup() as tg:
            for core_id, core in valid:
                tg.create_task(
                    core.ingest_state_update(update),
                    name=f"propagate-{core_id}",
                )
        log.debug("propagation: selective scope='%s' targets=%s",
                  update.scope, [c for c, _ in valid])
