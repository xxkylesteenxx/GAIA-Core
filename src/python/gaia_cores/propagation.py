"""Planetary state propagation.

Spec ref: PYTHON-ORCHESTRATION-SPEC §7
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .models import CoreMessage, StateUpdate

if TYPE_CHECKING:
    from .registry import CoreRegistry

log = logging.getLogger(__name__)


class StatePropagator:
    """Broadcasts or selectively delivers StateUpdates across cores."""

    def __init__(self, registry: "CoreRegistry") -> None:
        self._registry = registry

    async def broadcast(self, update: StateUpdate) -> None:
        """Deliver update to every registered core except the source.

        Spec ref: PYTHON-ORCHESTRATION-SPEC §7 — full broadcast.
        """
        cores = list(self._registry._cores.values())  # noqa: SLF001
        for core in cores:
            if core.name != update.source:
                if hasattr(core, "ingest_state_update"):
                    await core.ingest_state_update(update.scope, update.values)  # type: ignore[attr-defined]
                else:
                    msg = CoreMessage(
                        sender=update.source,
                        topic="gaia.state.broadcast/v1",
                        payload={"scope": update.scope, "values": update.values,
                                 "summary": update.summary},
                        trust_label="bounded",
                    )
                    await core.handle_message(msg)
        log.debug("propagation: broadcast from '%s' scope='%s'",
                  update.source, update.scope)

    async def selective(
        self,
        update: StateUpdate,
        *,
        targets: list[str],
    ) -> None:
        """Deliver update only to cores named in targets.

        Spec ref: PYTHON-ORCHESTRATION-SPEC §7 — selective delivery.
        """
        for tag in targets:
            core = self._registry.get(tag)
            if core is None:
                log.warning("propagation: unknown target '%s'", tag)
                continue
            if hasattr(core, "ingest_state_update"):
                await core.ingest_state_update(update.scope, update.values)  # type: ignore[attr-defined]
            else:
                msg = CoreMessage(
                    sender=update.source,
                    recipient=tag,
                    topic="gaia.state.selective/v1",
                    payload={"scope": update.scope, "values": update.values,
                             "summary": update.summary},
                    trust_label="bounded",
                )
                await core.handle_message(msg)
            log.debug("propagation: selective -> '%s' scope='%s'", tag, update.scope)
