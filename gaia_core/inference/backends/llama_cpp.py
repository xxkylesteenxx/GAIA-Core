"""llama.cpp backend — edge / offline inference.

Dependency: llama-cpp-python (optional, guarded import)
Fallback: raises NotImplementedError if not installed.
"""
from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from gaia_core.inference.contracts import InferBackend, InferRequest, InferResponse

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)

try:
    from llama_cpp import Llama  # type: ignore
    _LLAMA_AVAILABLE = True
except ImportError:
    _LLAMA_AVAILABLE = False
    Llama = None  # type: ignore


class LlamaCppBackend:
    """Thin wrapper around llama-cpp-python."""

    def __init__(self, model_path: str, n_ctx: int = 4096, n_gpu_layers: int = 0) -> None:
        if not _LLAMA_AVAILABLE:
            raise ImportError("llama-cpp-python is not installed. Run: pip install llama-cpp-python")
        self._llm = Llama(model_path=model_path, n_ctx=n_ctx, n_gpu_layers=n_gpu_layers, verbose=False)
        self._model_path = model_path

    def infer(self, request: InferRequest) -> InferResponse:
        t0 = time.monotonic()
        result = self._llm(
            request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            stream=False,
        )
        latency_ms = (time.monotonic() - t0) * 1000
        choice = result["choices"][0]
        usage = result.get("usage", {})
        return InferResponse(
            text=choice["text"],
            model_id=request.model_id,
            backend=InferBackend.LLAMA_CPP,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            latency_ms=latency_ms,
        )
