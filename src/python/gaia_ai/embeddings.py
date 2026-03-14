"""Embedding Engine.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §3, §5

The embedding layer uses a deterministic placeholder in this scaffold.
Replace HashEmbeddingEngine / DeterministicEmbeddingBackend with a
production backend (sentence-transformers, OpenAI embeddings, ONNX, etc.)
before any retrieval or semantic similarity work.

Public surface
--------------
EmbeddingRecord          — slots=True dataclass for a single embedding
HashEmbeddingEngine      — canonical deterministic placeholder (sync, direct)
EmbeddingBackend         — ABC for async production backends
DeterministicEmbeddingBackend — async wrapper around HashEmbeddingEngine
EmbeddingEngine          — high-level async interface used by RAGPipeline
"""

from __future__ import annotations

import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Sequence

log = logging.getLogger(__name__)

# Canonical default dimension for GAIA scaffold.
# HashEmbeddingEngine defaults to 32; EmbeddingEngine wrapper defaults to 384.
DEFAULT_DIM = 384


# ---------------------------------------------------------------------------
# EmbeddingRecord
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class EmbeddingRecord:
    """A single embedding result."""
    object_id: str
    vector:    list[float]
    text:      str
    modality:  str = "text"


# ---------------------------------------------------------------------------
# HashEmbeddingEngine  —  canonical deterministic placeholder (sync)
# ---------------------------------------------------------------------------

class HashEmbeddingEngine:
    """Deterministic placeholder embedding engine.

    Produces stable, unit-range vectors from SHA-256 of the input text.
    NOT semantically meaningful — suitable for:
      - unit tests that need stable vector identities
      - scaffold development without a GPU or model download

    Replace with SentenceTransformer or another backend in production.
    """

    def __init__(self, dims: int = 32) -> None:
        self.dims = dims

    def embed_text(self, object_id: str, text: str) -> EmbeddingRecord:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        floats = [
            ((digest[i % len(digest)] / 255.0) * 2.0) - 1.0
            for i in range(self.dims)
        ]
        return EmbeddingRecord(object_id=object_id, vector=floats, text=text)

    def embed_batch(
        self, items: list[tuple[str, str]]
    ) -> list[EmbeddingRecord]:
        return [self.embed_text(object_id, text) for object_id, text in items]


# ---------------------------------------------------------------------------
# EmbeddingBackend ABC  —  async interface for production backends
# ---------------------------------------------------------------------------

class EmbeddingBackend(ABC):
    """Abstract base for async embedding backends."""

    @abstractmethod
    async def encode(self, texts: Sequence[str]) -> list[list[float]]:
        """Return a list of float vectors, one per input text."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding vector dimension."""


class DeterministicEmbeddingBackend(EmbeddingBackend):
    """Async wrapper around HashEmbeddingEngine for use with EmbeddingEngine.

    Bridges the sync HashEmbeddingEngine into the async EmbeddingBackend ABC
    so that RAGPipeline and other async consumers can use it transparently.
    """

    def __init__(self, dim: int = DEFAULT_DIM) -> None:
        self._engine = HashEmbeddingEngine(dims=dim)

    @property
    def dimension(self) -> int:
        return self._engine.dims

    async def encode(self, texts: Sequence[str]) -> list[list[float]]:
        records = self._engine.embed_batch(
            [(str(i), t) for i, t in enumerate(texts)]
        )
        return [r.vector for r in records]


# ---------------------------------------------------------------------------
# EmbeddingEngine  —  high-level async interface used by RAGPipeline
# ---------------------------------------------------------------------------

class EmbeddingEngine:
    """High-level async embedding interface.

    Wraps any EmbeddingBackend and provides batch encoding with logging.
    Defaults to DeterministicEmbeddingBackend (HashEmbeddingEngine under the hood).
    """

    def __init__(self, backend: EmbeddingBackend | None = None) -> None:
        self._backend: EmbeddingBackend = backend or DeterministicEmbeddingBackend()

    @property
    def dimension(self) -> int:
        return self._backend.dimension

    async def encode(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        vectors = await self._backend.encode(texts)
        log.debug("embeddings: encoded %d text(s) dim=%d",
                  len(vectors), self._backend.dimension)
        return vectors

    async def encode_one(self, text: str) -> list[float]:
        results = await self.encode([text])
        return results[0]
