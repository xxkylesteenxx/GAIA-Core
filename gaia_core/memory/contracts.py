"""Core data contracts for the GAIA holographic memory stack.

MemoryAtom  — the atomic unit of stored memory
MemorySearchResult — a single ranked retrieval hit
"""
from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MemoryAtom:
    """The atomic unit of stored memory in GAIA.

    content      — raw text or structured payload
    embedding    — dense float vector (populated by ingestion pipeline)
    core         — originating consciousness core (NEXUS, SOPHIA, ATLAS …)
    atom_id      — stable UUID, auto-generated if not supplied
    timestamp_ns — wall-clock nanosecond timestamp at creation
    causal_id    — ID of the CausalEnvelope that wraps this atom
    tags         — free-form labels for filtering
    metadata     — arbitrary key-value store
    sha256       — content integrity digest (auto-computed)
    """
    content: str
    core: str
    embedding: list[float] = field(default_factory=list)
    atom_id: str = field(default_factory=lambda: f"atom_{uuid.uuid4().hex[:16]}")
    timestamp_ns: int = field(default_factory=time.time_ns)
    causal_id: str = ""
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    sha256: str = field(default="", compare=False)

    def __post_init__(self) -> None:
        if not self.sha256:
            self.sha256 = hashlib.sha256(self.content.encode()).hexdigest()

    def verify(self) -> bool:
        """Return True if content matches stored digest."""
        return hashlib.sha256(self.content.encode()).hexdigest() == self.sha256

    def to_dict(self) -> dict[str, Any]:
        return {
            "atom_id": self.atom_id,
            "content": self.content,
            "core": self.core,
            "embedding": self.embedding,
            "timestamp_ns": self.timestamp_ns,
            "causal_id": self.causal_id,
            "tags": self.tags,
            "metadata": self.metadata,
            "sha256": self.sha256,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryAtom":
        return cls(**data)


@dataclass
class MemorySearchResult:
    """A single ranked retrieval result from the memory fabric."""
    atom: MemoryAtom
    score: float          # cosine similarity or ANN distance (higher = more similar)
    tier: str             # "hot" | "capacity" | "archive"
    latency_ms: float = 0.0
    visible: bool = True  # False if causally gated out for this session
