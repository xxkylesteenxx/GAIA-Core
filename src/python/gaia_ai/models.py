"""Shared data models for gaia_ai.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0

Canonical types shared across the router, RAG pipeline, vector store,
and registry layers.

ModelProfile is defined here (not registry.py) and re-exported from
registry.py for backward compat.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# InferenceMode
# ---------------------------------------------------------------------------

class InferenceMode(str, Enum):
    """Declared inference mode for a query.

    Used by InferenceRouter to select the best profile.
    """
    FAST           = "fast"           # low-latency local fast route
    DEEP           = "deep"           # high-depth reasoning route
    EMBEDDING      = "embedding"      # embedding-only request
    GENERATION     = "generation"     # text generation (canonical default)
    RETRIEVAL      = "retrieval"      # retrieval-only step
    CHAT           = "chat"           # general conversational
    COMPLETION     = "completion"     # raw completion
    CODE           = "code"           # code generation / analysis
    SUMMARISATION  = "summarisation"  # summarisation task
    CLASSIFICATION = "classification" # classification task


# ---------------------------------------------------------------------------
# ModelProfile
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class ModelProfile:
    """Flat profile declaring everything needed to route and govern a model.

    Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §4

    This is the canonical definition. registry.py re-exports it for
    backward compat with existing code that imports from registry.
    """
    name:                  str
    backend:               str
    family:                str
    locality:              str
    min_vram_gb:           int   = 0
    min_system_ram_gb:     int   = 0
    context_window:        int   = 8192
    supports_streaming:    bool  = True
    supports_tool_use:     bool  = False
    supports_embeddings:   bool  = False
    supports_fine_tuning:  bool  = False
    trust_tier:            str   = "internal"
    notes:                 str   = ""
    tags:                  list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# QueryContext
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class QueryContext:
    """A routable query with policy metadata."""
    text:                  str
    user_id:               str            = "anonymous"
    mode:                  InferenceMode  = InferenceMode.GENERATION
    latency_budget_ms:     int            = 1500
    requires_private_data: bool           = False
    requires_tool_use:     bool           = False
    max_tokens:            int            = 512
    metadata:              dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# RouteDecision
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class RouteDecision:
    """The routing decision produced by InferenceRouter.decide()."""
    profile:             ModelProfile
    endpoint:            str
    reason:              str
    retrieval_required:  bool = False
    guard_scan_required: bool = True


# ---------------------------------------------------------------------------
# RetrievedChunk  (shared with RAG pipeline and vector store)
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class RetrievedChunk:
    """A single retrieved document chunk with similarity score."""
    doc_id:   str
    text:     str
    score:    float
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# GenerationResult
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class GenerationResult:
    """Structured output from a text generation call."""
    text:               str
    model_name:         str
    prompt_tokens:      int            = 0
    completion_tokens:  int            = 0
    metadata:           dict[str, Any] = field(default_factory=dict)
