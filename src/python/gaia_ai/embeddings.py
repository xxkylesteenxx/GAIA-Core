"""Embedding Engine.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §3, §5

The embedding layer uses a deterministic placeholder in this scaffold.
Replace DeterministicEmbeddingBackend with a production backend
(e.g. sentence-transformers, OpenAI embeddings, or a local ONNX model).
"""

from __future__ import annotations

import hashlib
import logging
import math
from abc import ABC, abstractmethod
from typing import Sequence

log = logging.getLogger(__name__)

# Canonical embedding dimension for GAIA scaffold.
# Production backends may use different dimensions; normalisation is applied.
DEFAULT_DIM = 384


class EmbeddingBackend(ABC):
    """Abstract base for embedding backends."""

    @abstractmethod
    async def encode(self, texts: Sequence[str]) -> list[list[float]]:
        """Return a list of float vectors, one per input text."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Embedding vector dimension."""


class DeterministicEmbeddingBackend(EmbeddingBackend):
    """Deterministic hash-based placeholder.

    NOT semantically meaningful. Intended for:
      - unit tests that need stable vector identities
      - scaffold development without a GPU or model download

    Replace with a real backend (sentence-transformers, OpenAI, ONNX, etc.)
    before any retrieval or semantic similarity work.
    """

    def __init__(self, dim: int = DEFAULT_DIM) -> None:
        self._dim = dim

    @property
    def dimension(self) -> int:
        return self._dim

    async def encode(self, texts: Sequence[str]) -> list[list[float]]:
        return [self._hash_embed(t) for t in texts]

    def _hash_embed(self, text: str) -> list[float]:
        """Produce a unit-normalised pseudo-random vector from SHA-256 of text."""
        digest = hashlib.sha256(text.encode()).digest()  # 32 bytes
        # Tile digest to fill dimension
        raw = []
        for i in range(self._dim):
            byte_val = digest[i % 32]
            raw.append(float(byte_val) - 127.5)
        norm = math.sqrt(sum(v * v for v in raw)) or 1.0
        return [v / norm for v in raw]


class EmbeddingEngine:
    """High-level embedding interface used by the RAG pipeline and router.

    Wraps any EmbeddingBackend and provides batch encoding with logging.
    """

    def __init__(self, backend: EmbeddingBackend | None = None) -> None:
        self._backend: EmbeddingBackend = backend or DeterministicEmbeddingBackend()

    @property
    def dimension(self) -> int:
        return self._backend.dimension

    async def encode(self, texts: Sequence[str]) -> list[list[float]]:
        """Encode one or more texts into embedding vectors."""
        if not texts:
            return []
        vectors = await self._backend.encode(texts)
        log.debug("embeddings: encoded %d text(s) dim=%d", len(vectors), self._backend.dimension)
        return vectors

    async def encode_one(self, text: str) -> list[float]:
        results = await self.encode([text])
        return results[0]
