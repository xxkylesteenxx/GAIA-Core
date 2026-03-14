"""In-memory vector store.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §5

The in-memory vector store in this scaffold should be replaced or
extended with FAISS / DiskANN / HNSW for persistent deployments.

Public surface
--------------
InMemoryVectorStore  —  cosine-similarity store backed by a dict[object_id, EmbeddingRecord]
                         O(1) upsert by object_id; O(n) linear scan for query.
"""

from __future__ import annotations

from math import sqrt

from .embeddings import EmbeddingRecord
from .models import RetrievedChunk


class InMemoryVectorStore:
    """Cosine-similarity vector store backed by a dict.

    Keyed by object_id — upsert replaces in O(1) vs O(n) list scan.
    Replace with FAISS / DiskANN / HNSW for production deployments.
    """

    def __init__(self) -> None:
        self._records: dict[str, EmbeddingRecord] = {}

    # ------------------------------------------------------------------ #
    # Ingestion                                                            #
    # ------------------------------------------------------------------ #

    def upsert(self, record: EmbeddingRecord) -> None:
        """Insert or replace a record by object_id."""
        self._records[record.object_id] = record

    def batch_upsert(self, records: list[EmbeddingRecord]) -> None:
        """Upsert a batch of EmbeddingRecords."""
        for record in records:
            self.upsert(record)

    # ------------------------------------------------------------------ #
    # Retrieval                                                            #
    # ------------------------------------------------------------------ #

    def query(
        self,
        query_vector: list[float],
        top_k: int = 4,
    ) -> list[RetrievedChunk]:
        """Return the top-k most similar chunks by cosine similarity.

        Chunk metadata includes the source record's modality field.
        """
        scored = []
        for record in self._records.values():
            score = self._cosine(query_vector, record.vector)
            scored.append(
                RetrievedChunk(
                    doc_id=record.object_id,
                    text=record.text,
                    score=score,
                    metadata={"modality": record.modality},
                )
            )
        return sorted(scored, key=lambda x: x.score, reverse=True)[:top_k]

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na  = sqrt(sum(x * x for x in a)) or 1.0
        nb  = sqrt(sum(y * y for y in b)) or 1.0
        return dot / (na * nb)

    @property
    def size(self) -> int:
        return len(self._records)

    def delete(self, object_id: str) -> None:
        """Remove a record by object_id. No-op if not present."""
        self._records.pop(object_id, None)

    def clear(self) -> None:
        """Remove all records."""
        self._records.clear()
