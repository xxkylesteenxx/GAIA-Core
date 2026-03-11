"""Unified inference contract for all GAIA backends.

No GAIA subsystem should import backend-specific APIs directly.
All calls go through InferRequest → router → backend → InferResponse.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any


class InferBackend(str, enum.Enum):
    """Available inference backends."""
    LLAMA_CPP = "llama_cpp"   # Edge / offline
    VLLM = "vllm"             # Server / high-context generative
    TRITON = "triton"         # Perception / embedding / classifier


@dataclass
class InferRequest:
    """A single inference request, backend-agnostic."""
    prompt: str
    model_id: str
    backend: InferBackend | None = None       # None = auto-route via policy
    max_tokens: int = 512
    temperature: float = 0.7
    stream: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class InferResponse:
    """A single inference response, backend-agnostic."""
    text: str
    model_id: str
    backend: InferBackend
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
