"""Planetary state propagation.

Spec ref: PYTHON-ORCHESTRATION-SPEC §7

Supports full broadcast, selective (by domain tag), and
policy-mediated delivery.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .models import CoreMessage, StateUpdate

if TYPE_CHECKING:
    from .registry import CoreRegistry

log = logging.getLogger(__name__)


class StatePropagator:
    """Broadcasts or selectively delivers StateUpdates across cores.

    Accepts a CoreRegistry directly; does not require a separate bus
    reference for broadcast delivery.
    """

    def __init__(self, registry: "CoreRegistry") -> None:
        self._registry = registry

    async def broadcast(self, update: StateUpdate) -> None:
        """Deliver update to every registered core.

        Spec ref: PYTHON-ORCHESTRATION-SPEC §7 — full broadcast.
        """
        msg = CoreMessage(
            sender=update.source,
            topic="gaia.state.broadcast/v1",
            payload={
                "scope":   update.scope,
                "values":  update.values,
                "summary": update.summary,
            },
            trust_label="bounded",
        )
        cores = list(self._registry._cores.values())  # noqa: SLF001
        for core in cores:
            if core.name != update.source:
                await core.handle_message(msg)
        log.debug("propagation: broadcast from '%s' scope='%s'",
                  update.source, update.scope)

    async def selective(
        self,
        update: StateUpdate,
        domain_tags: list[str],
    ) -> None:
        """Deliver update only to cores named in domain_tags.

        Spec ref: PYTHON-ORCHESTRATION-SPEC §7 — selective delivery.
        """
        for tag in domain_tags:
            core = self._registry.get(tag)
            if core is None:
                log.warning("propagation: unknown domain tag '%s'", tag)
                continue
            msg = CoreMessage(
                sender=update.source,
                recipient=tag,
                topic="gaia.state.selective/v1",
                payload={
                    "scope":   update.scope,
                    "values":  update.values,
                    "summary": update.summary,
                },
                trust_label="bounded",
            )
            await core.handle_message(msg)
