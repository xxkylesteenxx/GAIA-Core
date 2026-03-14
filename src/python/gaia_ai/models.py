"""Shared data models for gaia_ai.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0

Canonical types shared across the router, RAG pipeline, vector store,
and registry layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .registry import ModelProfile


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
    CHAT           = "chat"           # general conversational
    COMPLETION     = "completion"     # raw completion
    CODE           = "code"           # code generation / analysis
    SUMMARISATION  = "summarisation"  # summarisation task
    CLASSIFICATION = "classification" # classification task


# ---------------------------------------------------------------------------
# QueryContext
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class QueryContext:
    """A routable query with policy metadata."""
    text:                  str
    mode:                  InferenceMode   = InferenceMode.CHAT
    requires_private_data: bool            = False
    latency_budget_ms:     int             = 5000
    source:                str             = "user"
    metadata:              dict[str, Any]  = field(default_factory=dict)


# ---------------------------------------------------------------------------
# RouteDecision
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class RouteDecision:
    """The routing decision produced by InferenceRouter.decide()."""
    profile:              "ModelProfile"
    endpoint:             str
    reason:               str
    retrieval_required:   bool
    guard_scan_required:  bool


# ---------------------------------------------------------------------------
# RetrievedChunk  (shared with RAG pipeline)
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class RetrievedChunk:
    """A single retrieved document chunk with similarity score."""
    doc_id:   str
    text:     str
    score:    float
    metadata: dict[str, Any] = field(default_factory=dict)
