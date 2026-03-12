"""Unified inference contract for all GAIA backends.

No GAIA subsystem should import backend-specific APIs directly.
All calls go through InferRequest → router → backend → InferResponse.

Canonical types: RuntimeBackend, TaskType, InferRequest, InferResponse.
InferBackend is retained as a one-deprecation-cycle compatibility alias.
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Mapping


# ---------------------------------------------------------------------------
# Canonical backend enumeration
# ---------------------------------------------------------------------------

class RuntimeBackend(str, enum.Enum):
    """Canonical runtime backend selector (GAIA-SPEC-INF-001)."""
    AUTO       = "auto"        # router policy chooses
    MOCK       = "mock"        # in-process stub; always available for tests
    LLAMA_CPP  = "llama_cpp"   # edge / offline
    VLLM       = "vllm"        # server / high-context generative
    TRITON     = "triton"      # perception / embedding / classifier
    REMOTE_HTTP = "remote_http" # generic HTTP inference endpoint


# One-cycle compatibility alias — new code must use RuntimeBackend.
InferBackend = RuntimeBackend


# ---------------------------------------------------------------------------
# Task type enumeration
# ---------------------------------------------------------------------------

class TaskType(str, enum.Enum):
    """Canonical task type (GAIA-SPEC-INF-001)."""
    GENERATE    = "generate"
    EMBED       = "embed"
    CLASSIFY    = "classify"
    RERANK      = "rerank"
    SUMMARIZE   = "summarize"
    ROUTE       = "route"
    POLICY_EVAL = "policy_eval"


# ---------------------------------------------------------------------------
# Request / response dataclasses
# ---------------------------------------------------------------------------

@dataclass
class InferRequest:
    """A single inference request, backend-agnostic.

    Supports both the original Core LLM-oriented API (prompt/model_id) and
    the structured Server router API (task_type/payload/core_id).
    Both surfaces coexist; callers may populate whichever fits their context.
    """
    # --- structured router surface ---
    request_id: str = ""
    core_id: str = ""
    task_type: TaskType = TaskType.GENERATE
    backend: RuntimeBackend | None = None          # None / AUTO = policy-routed
    payload: Mapping[str, Any] = field(default_factory=dict)
    routing_hints: Mapping[str, Any] = field(default_factory=dict)
    timeout_ms: int = 30_000
    priority: int = 100

    # --- convenience LLM surface (legacy / ergonomic) ---
    prompt: str = ""
    model_id: str = ""
    max_tokens: int | None = None
    temperature: float | None = None
    stream: bool = False

    # --- causal chain ---
    trace_id: str | None = None        # causal log key; links to JetStream event
    continuity_id: str | None = None   # checkpoint epoch this call belongs to

    # --- open metadata ---
    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience constructors
    # ------------------------------------------------------------------

    @classmethod
    def for_generate(
        cls,
        *,
        request_id: str,
        core_id: str,
        prompt: str,
        backend: RuntimeBackend | None = None,
        model_id: str = "",
        max_tokens: int | None = None,
        temperature: float | None = None,
        **kwargs: Any,
    ) -> "InferRequest":
        return cls(
            request_id=request_id,
            core_id=core_id,
            task_type=TaskType.GENERATE,
            backend=backend,
            payload={"prompt": prompt},
            prompt=prompt,
            model_id=model_id,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs,
        )

    @classmethod
    def for_embed(
        cls,
        *,
        request_id: str,
        core_id: str,
        text: str | list[str],
        model_id: str = "",
        **kwargs: Any,
    ) -> "InferRequest":
        texts = text if isinstance(text, list) else [text]
        return cls(
            request_id=request_id,
            core_id=core_id,
            task_type=TaskType.EMBED,
            payload={"texts": texts},
            model_id=model_id,
            **kwargs,
        )


@dataclass
class InferResponse:
    """A single inference response, backend-agnostic."""
    # --- structured router surface ---
    request_id: str = ""
    accepted: bool = True
    core_id: str = ""
    task_type: TaskType = TaskType.GENERATE
    backend: RuntimeBackend = RuntimeBackend.MOCK
    model_id: str | None = None
    result: dict[str, Any] = field(default_factory=dict)
    usage: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None

    # --- convenience LLM surface (derived from result) ---
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0

    # --- open metadata ---
    metadata: dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------

    def text_output(self) -> str | None:
        """Return the generated text from a GENERATE response, or None."""
        return self.result.get("text")
