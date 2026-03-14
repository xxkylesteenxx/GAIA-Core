"""Shared data models for gaia_ai.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0

QueryContext and RetrievedChunk are the canonical types shared across
the RAG pipeline, vector store, and router layers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class QueryContext:
    """A retrieval query with optional metadata."""
    text:     str
    source:   str              = "user"
    metadata: dict[str, Any]  = field(default_factory=dict)


@dataclass(slots=True)
class RetrievedChunk:
    """A single retrieved document chunk with similarity score."""
    doc_id:   str
    text:     str
    score:    float
    metadata: dict[str, Any]  = field(default_factory=dict)
