"""Async inter-core message bus.

Spec ref: PYTHON-ORCHESTRATION-SPEC §6, §8

Implements positive-authorization routing: a message is delivered
only if an explicit allow entry exists for (sender, recipient, topic_prefix).
All other routes are rejected by default.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .models import CoreMessage

if TYPE_CHECKING:
    from .base import GaiaCore

log = logging.getLogger(__name__)


@dataclass
class RouteRule:
    """A single positive-authorization route entry."""
    sender: str
    recipient: str          # "*" matches any recipient (broadcast allow)
    topic_prefix: str


class CoreMessageBus:
    """Async message bus with positive-authorization route table."""

    def __init__(self) -> None:
        self._cores: dict[str, "GaiaCore"] = {}
        self._rules: list[RouteRule] = []

    # -- Registration ------------------------------------------------------

    def register(self, core: "GaiaCore") -> None:
        self._cores[core.name] = core

    def allow(self, sender: str, recipient: str, topic_prefix: str) -> None:
        """Add a positive-authorization route rule."""
        self._rules.append(RouteRule(sender=sender, recipient=recipient,
                                      topic_prefix=topic_prefix))

    # -- Dispatch ----------------------------------------------------------

    async def dispatch(self, msg: CoreMessage) -> None:
        """Route msg to its recipient(s), enforcing the allow-list."""
        if msg.is_broadcast():
            for name, core in self._cores.items():
                if name != msg.sender and self._authorized(msg.sender, name, msg.topic):
                    await self._deliver(core, msg)
        else:
            if not self._authorized(msg.sender, msg.recipient, msg.topic):  # type: ignore[arg-type]
                log.warning("bus: route denied %s -> %s [%s]",
                            msg.sender, msg.recipient, msg.topic)
                return
            core = self._cores.get(msg.recipient)  # type: ignore[arg-type]
            if core:
                await self._deliver(core, msg)

    async def _deliver(self, core: "GaiaCore", msg: CoreMessage) -> None:
        try:
            await core.handle_message(msg)
        except Exception:
            log.exception("bus: unhandled exception in %s.handle_message", core.name)

    def _authorized(self, sender: str, recipient: str, topic: str) -> bool:
        return any(
            r.sender == sender
            and (r.recipient == "*" or r.recipient == recipient)
            and topic.startswith(r.topic_prefix)
            for r in self._rules
        )
