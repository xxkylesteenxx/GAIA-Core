"""Causal broadcast queueing for GAIA inter-core messaging.

This module avoids package-level imports that would collide with the Python standard
library's ``platform`` module by loading the sibling ``vector_clock.py`` file directly
when needed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional
import importlib.util
import sys


def _load_vector_clock_class():
    module_path = Path(__file__).with_name("vector_clock.py")
    spec = importlib.util.spec_from_file_location("gaia_vector_clock", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load vector clock module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.VectorClock


VectorClock = _load_vector_clock_class()


@dataclass(slots=True)
class CausalMessage:
    sender: str
    topic: str
    payload: object
    clock: object
    message_id: str


@dataclass
class CausalBroadcaster:
    local_actor: str
    clock: object = field(default_factory=lambda: VectorClock())
    delivered: List[CausalMessage] = field(default_factory=list)
    pending: List[CausalMessage] = field(default_factory=list)

    def emit(self, topic: str, payload: object, message_id: str) -> CausalMessage:
        self.clock.tick(self.local_actor)
        return CausalMessage(
            sender=self.local_actor,
            topic=topic,
            payload=payload,
            clock=self.clock.copy(),
            message_id=message_id,
        )

    def receive(self, message: CausalMessage) -> bool:
        if self._deliverable(message):
            self._apply(message)
            self._drain_pending()
            return True
        self.pending.append(message)
        return False

    def _deliverable(self, message: CausalMessage) -> bool:
        local = self.clock
        remote = message.clock
        for actor, counter in remote.to_dict().items():
            expected = local.to_dict().get(actor, 0)
            if actor == message.sender:
                if counter != expected + 1:
                    return False
            elif counter > expected:
                return False
        return True

    def _apply(self, message: CausalMessage) -> None:
        self.clock = self.clock.merge(message.clock)
        self.delivered.append(message)

    def _drain_pending(self) -> None:
        made_progress = True
        while made_progress:
            made_progress = False
            next_pending: List[CausalMessage] = []
            for message in self.pending:
                if self._deliverable(message):
                    self._apply(message)
                    made_progress = True
                else:
                    next_pending.append(message)
            self.pending = next_pending
