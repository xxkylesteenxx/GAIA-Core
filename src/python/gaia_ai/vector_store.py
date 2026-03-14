"""In-memory vector store.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §5

The in-memory vector store in this scaffold should be replaced or
extended with FAISS / DiskANN / HNSW for persistent deployments.

Public surface
--------------
InMemoryVectorStore  —  cosine-similarity store backed by EmbeddingRecord list
"""

from __future__ import annotations

import math

from .embeddings import EmbeddingRecord
from .models import RetrievedChunk


class InMemoryVectorStore:
    """Cosine-similarity vector store backed by a Python list.

    Replace with FAISS / DiskANN / HNSW for production deployments.
    """

    def __init__(self) -> None:
        self._records: list[EmbeddingRecord] = []

    # ------------------------------------------------------------------ #
    # Ingestion                                                            #
    # ------------------------------------------------------------------ #

    def upsert(self, record: EmbeddingRecord) -> None:
        """Insert or replace a record by object_id."""
        for i, r in enumerate(self._records):
            if r.object_id == record.object_id:
                self._records[i] = record
                return
        self._records.append(record)

    def batch_upsert(self, records: list[EmbeddingRecord]) -> None:
        """Upsert a batch of records."""
        for record in records:
            self.upsert(record)

    # ------------------------------------------------------------------ #
    # Retrieval                                                            #
    # ------------------------------------------------------------------ #

    def query(
        self,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Return the top-k most similar chunks by cosine similarity."""
        if not self._records:
            return []
        scored = [
            (r, self._cosine(query_vector, r.vector))
            for r in self._records
        ]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [
            RetrievedChunk(doc_id=r.object_id, text=r.text, score=score)
            for r, score in scored[:top_k]
        ]

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na  = math.sqrt(sum(x * x for x in a)) or 1.0
        nb  = math.sqrt(sum(x * x for x in b)) or 1.0
        return dot / (na * nb)

    @property
    def size(self) -> int:
        return len(self._records)
