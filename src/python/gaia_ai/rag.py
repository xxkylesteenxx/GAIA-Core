"""Retrieval-Augmented Generation Pipeline.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §3, §4, §5

Retrieval SHALL execute before answer synthesis for knowledge-grounded
tasks unless explicitly bypassed by policy.

The in-memory vector store in this scaffold should be replaced or
extended with FAISS / DiskANN / HNSW for persistent deployments.
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from typing import Any, Sequence

from .embeddings import EmbeddingEngine
from .serving import ServingAdapter

log = logging.getLogger(__name__)


@dataclass
class Document:
    """A storable knowledge unit."""
    doc_id:   str
    content:  str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievedChunk:
    doc_id:    str
    content:   str
    score:     float
    metadata:  dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGResponse:
    answer:   str
    chunks:   list[RetrievedChunk]
    bypassed: bool = False   # True if retrieval was explicitly bypassed


class InMemoryVectorStore:
    """Simple cosine-similarity vector store backed by a Python list.

    Replace with FAISS / DiskANN / HNSW for production deployments.
    """

    def __init__(self) -> None:
        self._docs:    list[Document]     = []
        self._vectors: list[list[float]]  = []

    def add(self, doc: Document, vector: list[float]) -> None:
        self._docs.append(doc)
        self._vectors.append(vector)

    def search(self, query_vector: list[float], top_k: int = 5) -> list[RetrievedChunk]:
        if not self._vectors:
            return []
        scores = [
            (i, self._cosine(query_vector, v))
            for i, v in enumerate(self._vectors)
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        return [
            RetrievedChunk(
                doc_id=self._docs[i].doc_id,
                content=self._docs[i].content,
                score=score,
                metadata=self._docs[i].metadata,
            )
            for i, score in scores[:top_k]
        ]

    @staticmethod
    def _cosine(a: list[float], b: list[float]) -> float:
        dot  = sum(x * y for x, y in zip(a, b))
        na   = math.sqrt(sum(x * x for x in a)) or 1.0
        nb   = math.sqrt(sum(x * x for x in b)) or 1.0
        return dot / (na * nb)

    @property
    def size(self) -> int:
        return len(self._docs)


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline.

    Flow:
      1. Embed query
      2. Retrieve top-k chunks (unless bypass_retrieval=True)
      3. Build augmented prompt
      4. Synthesise answer via serving adapter

    Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §4 —
    Retrieval SHALL execute before answer synthesis for knowledge-grounded
    tasks unless explicitly bypassed by policy.
    """

    PROMPT_TEMPLATE = (
        "You are GAIA, a planetary intelligence assistant.\n"
        "Use the following retrieved context to answer the question.\n\n"
        "Context:\n{context}\n\n"
        "Question: {question}\n\n"
        "Answer:"
    )

    def __init__(
        self,
        embedding_engine: EmbeddingEngine,
        serving_adapter:  ServingAdapter,
        vector_store:     InMemoryVectorStore | None = None,
        top_k:            int = 5,
    ) -> None:
        self._embeddings  = embedding_engine
        self._adapter     = serving_adapter
        self._store       = vector_store or InMemoryVectorStore()
        self._top_k       = top_k

    async def ingest(self, documents: Sequence[Document]) -> None:
        """Embed and store documents into the vector store."""
        texts   = [d.content for d in documents]
        vectors = await self._embeddings.encode(texts)
        for doc, vec in zip(documents, vectors):
            self._store.add(doc, vec)
        log.info("rag: ingested %d document(s), store size=%d",
                 len(documents), self._store.size)

    async def query(
        self,
        question: str,
        *,
        bypass_retrieval: bool = False,
        max_tokens: int = 512,
    ) -> RAGResponse:
        """Answer a question with optional retrieval augmentation."""
        if bypass_retrieval:
            log.info("rag: retrieval bypassed by policy")
            answer = await self._adapter.infer(question, max_tokens=max_tokens)
            return RAGResponse(answer=answer, chunks=[], bypassed=True)

        query_vec = await self._embeddings.encode_one(question)
        chunks    = self._store.search(query_vec, top_k=self._top_k)

        context = "\n---\n".join(
            f"[{c.doc_id}] {c.content}" for c in chunks
        ) or "No relevant context found."

        prompt = self.PROMPT_TEMPLATE.format(
            context=context, question=question
        )
        answer = await self._adapter.infer(prompt, max_tokens=max_tokens)
        log.info("rag: query answered using %d chunk(s)", len(chunks))
        return RAGResponse(answer=answer, chunks=chunks)
