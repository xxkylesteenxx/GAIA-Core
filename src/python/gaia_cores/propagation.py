"""Planetary state propagation.

Spec ref: PYTHON-ORCHESTRATION-SPEC §7

Supports full broadcast, selective (by domain tag), and
policy-mediated delivery via the CoreMessageBus.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from .models import StateSnapshot

if TYPE_CHECKING:
    from .bus import CoreMessageBus
    from .registry import CoreRegistry

log = logging.getLogger(__name__)


class StatePropagator:
    """Broadcasts or selectively delivers state updates across cores."""

    def __init__(self, registry: "CoreRegistry", bus: "CoreMessageBus") -> None:
        self._registry = registry
        self._bus = bus

    async def broadcast(self, snapshot: StateSnapshot) -> None:
        """Deliver snapshot to every core except the originator."""
        from .models import CoreMessage
        msg = CoreMessage(
            sender=snapshot.core_name,
            topic="gaia.state.broadcast/v1",
            payload={"snapshot": snapshot.state, "health": snapshot.health.value},
            trust_label="bounded",
        )
        await self._bus.dispatch(msg)
        log.debug("propagation: broadcast from %s", snapshot.core_name)

    async def selective(
        self,
        snapshot: StateSnapshot,
        domain_tags: list[str],
    ) -> None:
        """Deliver snapshot only to cores whose name is in domain_tags."""
        from .models import CoreMessage
        for tag in domain_tags:
            core = self._registry.get(tag)
            if core is None:
                log.warning("propagation: unknown domain tag '%s'", tag)
                continue
            msg = CoreMessage(
                sender=snapshot.core_name,
                recipient=tag,
                topic="gaia.state.selective/v1",
                payload={"snapshot": snapshot.state, "health": snapshot.health.value},
                trust_label="bounded",
            )
            await self._bus.dispatch(msg)
