"""vLLM backend — server-tier high-context generative inference.

Dependency: vllm (optional, guarded import)
Assumes vLLM is running as an OpenAI-compatible server.
"""
from __future__ import annotations

import logging
import time

from gaia_core.inference.contracts import InferBackend, InferRequest, InferResponse

log = logging.getLogger(__name__)

try:
    import openai  # type: ignore
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False
    openai = None  # type: ignore


class VLLMBackend:
    """vLLM backend via OpenAI-compatible HTTP API."""

    def __init__(self, base_url: str = "http://localhost:8000/v1", api_key: str = "EMPTY") -> None:
        if not _OPENAI_AVAILABLE:
            raise ImportError("openai package is required for VLLMBackend. Run: pip install openai")
        self._client = openai.OpenAI(base_url=base_url, api_key=api_key)

    def infer(self, request: InferRequest) -> InferResponse:
        t0 = time.monotonic()
        completion = self._client.completions.create(
            model=request.model_id,
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        latency_ms = (time.monotonic() - t0) * 1000
        usage = completion.usage
        return InferResponse(
            text=completion.choices[0].text,
            model_id=request.model_id,
            backend=InferBackend.VLLM,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            latency_ms=latency_ms,
        )
