"""Causal dependency resolver for the GAIA memory stack.

Before delivering an atom to a consumer, verifies that all
causal dependencies (listed in CausalEnvelope.dependencies)
have already been delivered / are visible.

Holdback queue: atoms whose dependencies are unsatisfied are
buffered until dependencies arrive, then released in causal order.
"""
from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from threading import Lock
from typing import Callable

from gaia_core.memory.contracts import MemoryAtom
from gaia_core.memory.causal_envelope import CausalEnvelope

log = logging.getLogger(__name__)


@dataclass
class PendingAtom:
    atom: MemoryAtom
    envelope: CausalEnvelope
    unsatisfied: set[str] = field(default_factory=set)


class DependencyResolver:
    """Tracks delivered atoms and resolves causal holdback."""

    def __init__(self, on_deliver: Callable[[MemoryAtom], None] | None = None) -> None:
        self._delivered: set[str] = set()        # atom_ids already delivered
        self._holdback: dict[str, PendingAtom] = {}  # atom_id -> pending
        self._waiting_on: dict[str, list[str]] = defaultdict(list)  # dep_id -> [atom_ids waiting]
        self._lock = Lock()
        self._on_deliver = on_deliver or (lambda _: None)

    def submit(self, atom: MemoryAtom, envelope: CausalEnvelope) -> list[MemoryAtom]:
        """Submit an atom for delivery. Returns list of newly deliverable atoms."""
        with self._lock:
            unsatisfied = {
                dep for dep in envelope.dependencies
                if dep not in self._delivered
            }
            if not unsatisfied:
                return self._deliver_chain(atom, envelope)
            else:
                log.debug(
                    "Holding back atom %s waiting on %d deps: %s",
                    atom.atom_id, len(unsatisfied), unsatisfied,
                )
                self._holdback[atom.atom_id] = PendingAtom(
                    atom=atom, envelope=envelope, unsatisfied=unsatisfied
                )
                for dep in unsatisfied:
                    self._waiting_on[dep].append(atom.atom_id)
                return []

    def _deliver_chain(self, atom: MemoryAtom, envelope: CausalEnvelope) -> list[MemoryAtom]:
        """Deliver atom and cascade to any newly unblocked atoms."""
        delivered: list[MemoryAtom] = [atom]
        self._delivered.add(atom.atom_id)
        self._on_deliver(atom)
        # Check if delivering this atom unblocks others
        newly_unblocked = self._waiting_on.pop(atom.atom_id, [])
        for waiting_id in newly_unblocked:
            pending = self._holdback.get(waiting_id)
            if pending is None:
                continue
            pending.unsatisfied.discard(atom.atom_id)
            if not pending.unsatisfied:
                del self._holdback[waiting_id]
                delivered.extend(
                    self._deliver_chain(pending.atom, pending.envelope)
                )
        return delivered

    def is_delivered(self, atom_id: str) -> bool:
        with self._lock:
            return atom_id in self._delivered

    def holdback_depth(self) -> int:
        with self._lock:
            return len(self._holdback)
