"""Retrieval-Augmented Generation Pipeline.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §3, §4, §5

Retrieval SHALL execute before answer synthesis for knowledge-grounded
tasks unless explicitly bypassed by policy.

Two pipeline variants are provided:

  RAGPipeline       —  canonical sync pipeline (spec-primary)
                       Uses HashEmbeddingEngine + InMemoryVectorStore directly.
                       No serving adapter — returns the augmented prompt
                       for the caller to dispatch via InferenceRouter.

  RAGPipelineAsync  —  async variant for use with EmbeddingEngine (ABC-backed)
                       and a ServingAdapter. Produces a RAGResponse with
                       the synthesised answer included.

For production: replace InMemoryVectorStore with FAISS / DiskANN / HNSW.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Sequence

from .embeddings import EmbeddingEngine, HashEmbeddingEngine
from .models import QueryContext, RetrievedChunk
from .serving.base import ServingAdapter
from .vector_store import InMemoryVectorStore

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Legacy Document type — kept for backward compat with existing tests
# ---------------------------------------------------------------------------

@dataclass
class Document:
    """A storable knowledge unit (legacy; prefer QueryContext + EmbeddingRecord)."""
    doc_id:   str
    content:  str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGResponse:
    """Result of an async RAG query including synthesised answer."""
    answer:   str
    chunks:   list[RetrievedChunk]
    bypassed: bool = False


# ---------------------------------------------------------------------------
# RAGPipeline  —  canonical sync pipeline (spec-primary)
# ---------------------------------------------------------------------------

class RAGPipeline:
    """Canonical sync RAG pipeline.

    Uses HashEmbeddingEngine and InMemoryVectorStore directly.
    Does not call a serving adapter — returns the augmented prompt
    for the caller to dispatch via InferenceRouter.

    Spec ref: GAIA-AI-INFERENCE-SPEC v1.0
    """

    def __init__(
        self,
        embedding_engine: HashEmbeddingEngine,
        vector_store:     InMemoryVectorStore,
    ) -> None:
        self.embedding_engine = embedding_engine
        self.vector_store     = vector_store

    def index_documents(self, docs: list[tuple[str, str]]) -> None:
        """Embed and index a batch of (object_id, text) pairs."""
        records = self.embedding_engine.embed_batch(docs)
        self.vector_store.batch_upsert(records)

    def retrieve(
        self,
        query: QueryContext,
        top_k: int = 4,
    ) -> list[RetrievedChunk]:
        """Embed the query and return the top-k most similar chunks."""
        query_record = self.embedding_engine.embed_text(
            object_id="query", text=query.text
        )
        return self.vector_store.query(query_record.vector, top_k=top_k)

    def build_augmented_prompt(
        self,
        query:  QueryContext,
        chunks: list[RetrievedChunk],
    ) -> str:
        """Build a prompt string augmented with retrieved context."""
        context_blocks = "\n\n".join(
            f"[doc:{chunk.doc_id} score={chunk.score:.3f}]\n{chunk.text}"
            for chunk in chunks
        )
        return (
            "Use the following retrieved context when relevant.\n\n"
            f"{context_blocks}\n\n"
            f"User query: {query.text}"
        )


# ---------------------------------------------------------------------------
# RAGPipelineAsync  —  async variant for EmbeddingEngine + ServingAdapter
# ---------------------------------------------------------------------------

class RAGPipelineAsync:
    """Async RAG pipeline for use with EmbeddingEngine (ABC-backed) and ServingAdapter.

    Produces a RAGResponse containing the synthesised answer.
    Use this variant when integrating with OpenAIAdapter, TritonAdapter,
    or any other async serving backend.

    Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §4 —
    Retrieval SHALL execute before answer synthesis unless bypassed by policy.
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
        self._embeddings = embedding_engine
        self._adapter    = serving_adapter
        self._store      = vector_store or InMemoryVectorStore()
        self._top_k      = top_k

    async def ingest(self, documents: Sequence[Document]) -> None:
        """Embed and store Document objects into the vector store."""
        texts   = [d.content for d in documents]
        vectors = await self._embeddings.encode(texts)
        from .embeddings import EmbeddingRecord
        for doc, vec in zip(documents, vectors):
            self._store.upsert(
                EmbeddingRecord(object_id=doc.doc_id, vector=vec, text=doc.content)
            )
        log.info("rag: ingested %d document(s), store size=%d",
                 len(documents), self._store.size)

    async def query(
        self,
        question: str,
        *,
        bypass_retrieval: bool = False,
        max_tokens: int = 512,
    ) -> RAGResponse:
        """Answer a question, optionally with retrieval augmentation."""
        if bypass_retrieval:
            log.info("rag: retrieval bypassed by policy")
            answer = await self._adapter.infer(question, max_tokens=max_tokens)
            return RAGResponse(answer=answer, chunks=[], bypassed=True)

        qctx   = QueryContext(text=question)
        # Use sync vector store query via inline embed
        from .embeddings import EmbeddingRecord
        vec    = (await self._embeddings.encode([question]))[0]
        chunks = self._store.query(vec, top_k=self._top_k)

        context = "\n---\n".join(
            f"[{c.doc_id}] {c.text}" for c in chunks
        ) or "No relevant context found."

        prompt = self.PROMPT_TEMPLATE.format(context=context, question=question)
        answer = await self._adapter.infer(prompt, max_tokens=max_tokens)
        log.info("rag: query answered using %d chunk(s)", len(chunks))
        return RAGResponse(answer=answer, chunks=chunks)
