"""Serving Adapters.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §3, §5

Includes:
  ServingAdapter   — abstract base
  OpenAIAdapter    — OpenAI-compatible adapter (vLLM / local OpenAI-API server)
  TritonAdapter    — Triton Inference Server placeholder
  StubAdapter      — deterministic stub for tests and demos
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

log = logging.getLogger(__name__)


class ServingAdapter(ABC):
    """Abstract base for all serving backends."""

    @abstractmethod
    async def infer(self, prompt: str, *, max_tokens: int = 512, **kwargs: Any) -> str:
        """Run inference and return the generated text."""

    @abstractmethod
    async def health(self) -> bool:
        """Return True if the backend is reachable and ready."""


class OpenAIAdapter(ServingAdapter):
    """OpenAI-compatible adapter.

    Suitable for:
      - vLLM local serving  (`vllm serve <model> --api-key none`)
      - any OpenAI API-compatible server (LM Studio, llama.cpp server, etc.)
      - OpenAI cloud API (requires approved external route in registry)

    Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §5
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000/v1",
        api_key:  str = "none",
        model:    str = "default",
        timeout:  float = 30.0,
    ) -> None:
        self.base_url = base_url
        self.api_key  = api_key
        self.model    = model
        self.timeout  = timeout

    async def infer(self, prompt: str, *, max_tokens: int = 512, **kwargs: Any) -> str:
        """POST /v1/chat/completions and return the first choice content.

        Requires: pip install openai
        The openai package is an optional dependency; import is deferred to
        avoid hard-requiring it in scaffold deployments.
        """
        try:
            from openai import AsyncOpenAI  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "openai package is required for OpenAIAdapter: pip install openai"
            ) from exc

        client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)
        response = await client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            **kwargs,
        )
        return response.choices[0].message.content or ""

    async def health(self) -> bool:
        try:
            from openai import AsyncOpenAI  # type: ignore[import]
            client = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)
            models = await client.models.list()
            return len(models.data) > 0
        except Exception as exc:
            log.debug("OpenAIAdapter.health: %s", exc)
            return False


class TritonAdapter(ServingAdapter):
    """Triton Inference Server adapter placeholder.

    Suitable for high-throughput or ensemble model deployments.
    Replace stub with tritonclient.grpc / tritonclient.http in production.

    Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §5
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        model_name: str = "gaia_model",
    ) -> None:
        self.base_url   = base_url
        self.model_name = model_name
        log.warning(
            "TritonAdapter: production tritonclient bindings not installed — "
            "using stub. Replace with tritonclient.grpc for real deployments."
        )

    async def infer(self, prompt: str, *, max_tokens: int = 512, **kwargs: Any) -> str:
        # TODO: replace with tritonclient.grpc.aio inference call
        log.debug("TritonAdapter.infer: stub returning echo for model '%s'", self.model_name)
        return f"[TRITON-STUB] {prompt[:80]}"

    async def health(self) -> bool:
        # TODO: replace with GET /v2/health/ready
        return False


class StubAdapter(ServingAdapter):
    """Deterministic stub adapter for tests and demos.

    Returns a predictable response string so tests can assert on content
    without a live model server.
    """

    def __init__(self, response: str = "[STUB]") -> None:
        self.response = response
        self._call_count = 0

    async def infer(self, prompt: str, *, max_tokens: int = 512, **kwargs: Any) -> str:
        self._call_count += 1
        return f"{self.response} prompt={prompt[:40]!r}"

    async def health(self) -> bool:
        return True

    @property
    def call_count(self) -> int:
        return self._call_count
