"""CausalEnvelope — HLC-stamped causal metadata wrapper for MemoryAtoms.

Every atom entering the memory fabric is wrapped in a CausalEnvelope
that records:
  - HLC timestamp (wall + logical counter)
  - originating node and core
  - dependency set (IDs of atoms this one causally depends on)
  - trace ID for distributed tracing

This is distinct from gaia_core.models.CausalEnvelope (which is the
legacy continuity-layer envelope). This one is HLC-native and
specific to the memory stack.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CausalEnvelope:
    """HLC-stamped causal metadata for a MemoryAtom."""
    atom_id: str
    node_id: str
    core: str
    hlc_wall_ns: int          # physical wall clock at emission (nanoseconds)
    hlc_logical: int          # logical counter for same-ms disambiguation
    dependencies: list[str] = field(default_factory=list)  # atom_ids this depends on
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def hlc_tuple(self) -> tuple[int, int]:
        """(wall_ns, logical) — total order comparator."""
        return (self.hlc_wall_ns, self.hlc_logical)

    def happens_before(self, other: "CausalEnvelope") -> bool:
        """True if self causally precedes other."""
        return self.hlc_tuple < other.hlc_tuple

    def is_dependency_of(self, other: "CausalEnvelope") -> bool:
        """True if self.atom_id is in other’s explicit dependency set."""
        return self.atom_id in other.dependencies

    def to_dict(self) -> dict[str, Any]:
        return {
            "atom_id": self.atom_id,
            "node_id": self.node_id,
            "core": self.core,
            "hlc_wall_ns": self.hlc_wall_ns,
            "hlc_logical": self.hlc_logical,
            "dependencies": self.dependencies,
            "trace_id": self.trace_id,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CausalEnvelope":
        return cls(**data)
