"""GAIA AI inference orchestration pack."""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
from .models import (
    InferenceMode,
    QueryContext,
    RetrievedChunk,
    RouteDecision,
)

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------
from .registry import (
    HardwareMinima,
    Locality,
    ModelProfile,
    ModelProfileRegistry,
)

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
from .router import (
    InferenceRequest,
    InferenceResponse,
    InferenceRouter,
    InferenceRouterAsync,
    RoutingError,
    TaskMode,
)

# ---------------------------------------------------------------------------
# Serving
# ---------------------------------------------------------------------------
from .serving import (
    OpenAIAdapter,
    ServingAdapter,
    StubAdapter,
    TritonAdapter,
)

# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------
from .embeddings import (
    DeterministicEmbeddingBackend,
    EmbeddingBackend,
    EmbeddingEngine,
    EmbeddingRecord,
    HashEmbeddingEngine,
)

# ---------------------------------------------------------------------------
# Vector store
# ---------------------------------------------------------------------------
from .vector_store import InMemoryVectorStore

# ---------------------------------------------------------------------------
# RAG
# ---------------------------------------------------------------------------
from .rag import (
    Document,
    RAGPipeline,
    RAGPipelineAsync,
    RAGResponse,
)

# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------
from .training import (
    FineTuneEmitter,
    FinetuneEvent,
    FinetuneEventType,
    InMemoryEventSink,
)

# ---------------------------------------------------------------------------
# Robustness
# ---------------------------------------------------------------------------
from .robustness import (
    BUILTIN_PROBES,
    RobustnessScan,
    RobustnessScanner,
    ScanCategory,
    ScanReport,
    ScanResult,
)

__all__ = [
    # models
    "InferenceMode",
    "QueryContext",
    "RetrievedChunk",
    "RouteDecision",
    # registry
    "HardwareMinima",
    "Locality",
    "ModelProfile",
    "ModelProfileRegistry",
    # router
    "InferenceRequest",
    "InferenceResponse",
    "InferenceRouter",
    "InferenceRouterAsync",
    "RoutingError",
    "TaskMode",
    # serving
    "OpenAIAdapter",
    "ServingAdapter",
    "StubAdapter",
    "TritonAdapter",
    # embeddings
    "DeterministicEmbeddingBackend",
    "EmbeddingBackend",
    "EmbeddingEngine",
    "EmbeddingRecord",
    "HashEmbeddingEngine",
    # vector store
    "InMemoryVectorStore",
    # rag
    "Document",
    "RAGPipeline",
    "RAGPipelineAsync",
    "RAGResponse",
    # training
    "FineTuneEmitter",
    "FinetuneEvent",
    "FinetuneEventType",
    "InMemoryEventSink",
    # robustness
    "BUILTIN_PROBES",
    "RobustnessScan",
    "RobustnessScanner",
    "ScanCategory",
    "ScanReport",
    "ScanResult",
]
