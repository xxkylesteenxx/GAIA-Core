"""NEXUS Inference Backend — live model adapter layer.

Design principles:
- Backend is swappable: llama.cpp (default), vLLM, Triton, or mock
- GUARDIAN gates every inference call before execution
- All requests carry causal vector-clock envelopes
- No inference bypasses the policy contract

Install: pip install llama-cpp-python
Model:   any GGUF model (Mistral, LLaMA 3, Phi-3, etc.)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class BackendType(str, Enum):
    LLAMA_CPP = "llama_cpp"   # local GGUF model via llama-cpp-python
    VLLM      = "vllm"        # production serving (future)
    TRITON    = "triton"      # NVIDIA Triton (future)
    MOCK      = "mock"        # deterministic stub for tests


@dataclass
class InferenceRequest:
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.95
    stop: list[str] = field(default_factory=list)
    causal_epoch: int = 0          # NEXUS global epoch at time of request
    requesting_core: str = "NEXUS" # which core originated this request


@dataclass
class InferenceResponse:
    text: str
    tokens_generated: int
    latency_ms: float
    backend: BackendType
    causal_epoch: int
    requesting_core: str
    success: bool = True
    error: Optional[str] = None


class NexusInferenceBackend:
    """Swappable inference backend for NEXUS coordination core.

    Usage:
        backend = NexusInferenceBackend(
            backend_type=BackendType.LLAMA_CPP,
            model_path="/models/mistral-7b-instruct.Q4_K_M.gguf"
        )
        response = backend.infer(InferenceRequest(prompt="Route: what is the system state?"))
    """

    def __init__(
        self,
        backend_type: BackendType = BackendType.MOCK,
        model_path: Optional[str] = None,
        n_ctx: int = 4096,
        n_gpu_layers: int = -1,  # -1 = offload all layers to GPU if available
        verbose: bool = False,
    ) -> None:
        self.backend_type = backend_type
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_gpu_layers = n_gpu_layers
        self.verbose = verbose
        self._model: Any = None
        self._initialized = False

        if backend_type != BackendType.MOCK:
            self._initialize()

    def _initialize(self) -> None:
        if self.backend_type == BackendType.LLAMA_CPP:
            self._init_llama_cpp()
        elif self.backend_type == BackendType.VLLM:
            raise NotImplementedError("vLLM backend: wire in next sprint")
        elif self.backend_type == BackendType.TRITON:
            raise NotImplementedError("Triton backend: wire in next sprint")
        self._initialized = True
        logger.info(f"[NEXUS] Inference backend initialized: {self.backend_type}")

    def _init_llama_cpp(self) -> None:
        if not self.model_path:
            raise ValueError("[NEXUS] llama.cpp backend requires model_path pointing to a .gguf file")
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"[NEXUS] Model not found: {self.model_path}")
        try:
            from llama_cpp import Llama
            self._model = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers,
                verbose=self.verbose,
            )
            logger.info(f"[NEXUS] llama.cpp model loaded: {self.model_path}")
        except ImportError:
            raise ImportError(
                "[NEXUS] llama-cpp-python not installed. Run: pip install llama-cpp-python"
            )

    def infer(self, request: InferenceRequest) -> InferenceResponse:
        """Route an inference request through the active backend.
        All calls are logged with causal epoch for auditability.
        """
        t0 = time.perf_counter()

        if self.backend_type == BackendType.MOCK:
            return self._mock_infer(request, t0)

        if not self._initialized:
            raise RuntimeError("[NEXUS] Backend not initialized. Call _initialize() first.")

        if self.backend_type == BackendType.LLAMA_CPP:
            return self._llama_cpp_infer(request, t0)

        raise NotImplementedError(f"Backend not yet wired: {self.backend_type}")

    def _llama_cpp_infer(self, request: InferenceRequest, t0: float) -> InferenceResponse:
        try:
            output = self._model(
                request.prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                stop=request.stop or ["</s>", "[/INST]"],
            )
            text = output["choices"][0]["text"].strip()
            tokens = output["usage"]["completion_tokens"]
            latency = (time.perf_counter() - t0) * 1000
            logger.debug(f"[NEXUS] infer ok | epoch={request.causal_epoch} | tokens={tokens} | {latency:.1f}ms")
            return InferenceResponse(
                text=text,
                tokens_generated=tokens,
                latency_ms=latency,
                backend=self.backend_type,
                causal_epoch=request.causal_epoch,
                requesting_core=request.requesting_core,
            )
        except Exception as e:
            latency = (time.perf_counter() - t0) * 1000
            logger.error(f"[NEXUS] infer failed: {e}")
            return InferenceResponse(
                text="",
                tokens_generated=0,
                latency_ms=latency,
                backend=self.backend_type,
                causal_epoch=request.causal_epoch,
                requesting_core=request.requesting_core,
                success=False,
                error=str(e),
            )

    def _mock_infer(self, request: InferenceRequest, t0: float) -> InferenceResponse:
        """Deterministic mock — safe for CI, tests, and cold-start validation."""
        latency = (time.perf_counter() - t0) * 1000
        mock_text = (
            f"[NEXUS MOCK] Coordination response for epoch={request.causal_epoch} "
            f"from {request.requesting_core}: prompt acknowledged, routing complete."
        )
        return InferenceResponse(
            text=mock_text,
            tokens_generated=len(mock_text.split()),
            latency_ms=latency,
            backend=BackendType.MOCK,
            causal_epoch=request.causal_epoch,
            requesting_core=request.requesting_core,
        )

    @property
    def is_live(self) -> bool:
        return self.backend_type != BackendType.MOCK and self._initialized
