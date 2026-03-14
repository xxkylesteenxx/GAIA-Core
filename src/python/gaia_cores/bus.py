"""GAIA async message bus.

Spec ref: PYTHON-ORCHESTRATION-SPEC §6, §8

Implements a topic-keyed pub/sub bus.
Handlers subscribe to a route string (core_id or topic).
Publish delivers to all subscribers of message.recipient,
or to all subscribers for a broadcast (recipient=None).

Note: This bus does not enforce positive-authorization route rules
internally — route policy enforcement is the caller's responsibility
(e.g. via CoreRegistry.send or an external policy check by GUARDIAN).
"""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable

from .models import GaiaMessage

log = logging.getLogger(__name__)

Handler = Callable[[GaiaMessage], Awaitable[None]]


class GaiaMessageBus:
    """Async publish/subscribe message bus keyed by route string.

    Routes are typically core_id values (e.g. 'GUARDIAN', 'SOPHIA')
    or topic prefixes for wildcard subscribers.

    Thread/task safety: all mutations are guarded by an asyncio.Lock.
    """

    def __init__(self) -> None:
        self._subscribers: defaultdict[str, list[Handler]] = defaultdict(list)
        self._lock = asyncio.Lock()

    # -- Subscription ------------------------------------------------------

    async def subscribe(self, route: str, handler: Handler) -> None:
        """Register handler to receive messages published to route."""
        async with self._lock:
            self._subscribers[route].append(handler)
        log.debug("bus: subscribed handler to route '%s'", route)

    async def unsubscribe(self, route: str, handler: Handler) -> None:
        """Remove a previously registered handler from route."""
        async with self._lock:
            handlers = self._subscribers.get(route, [])
            try:
                handlers.remove(handler)
            except ValueError:
                pass

    # -- Publish -----------------------------------------------------------

    async def publish(self, message: GaiaMessage) -> None:
        """Deliver message to all matching subscribers.

        - If message.recipient is None: broadcast to ALL subscribers.
        - Otherwise: deliver only to subscribers of message.recipient.

        Exceptions from individual handlers are logged but do not
        prevent delivery to other subscribers.
        """
        recipients = await self._resolve_handlers(message)
        if not recipients:
            log.debug("bus: no subscribers for route '%s'", message.recipient or "<broadcast>")
            return
        results = await asyncio.gather(
            *(handler(message) for handler in recipients),
            return_exceptions=True,
        )
        for handler, result in zip(recipients, results):
            if isinstance(result, BaseException):
                log.exception(
                    "bus: handler %r raised on topic '%s': %s",
                    handler, message.topic, result,
                )

    async def _resolve_handlers(self, message: GaiaMessage) -> list[Handler]:
        async with self._lock:
            if message.recipient is None:
                # Broadcast: flatten all subscriber lists, deduplicate order-preserving
                seen: set[int] = set()
                flat: list[Handler] = []
                for handlers in self._subscribers.values():
                    for h in handlers:
                        if id(h) not in seen:
                            seen.add(id(h))
                            flat.append(h)
                return flat
            return list(self._subscribers.get(message.recipient, []))

    # -- Introspection -----------------------------------------------------

    async def routes(self) -> list[str]:
        """Return all currently registered route keys."""
        async with self._lock:
            return list(self._subscribers.keys())

    async def subscriber_count(self, route: str) -> int:
        async with self._lock:
            return len(self._subscribers.get(route, []))
