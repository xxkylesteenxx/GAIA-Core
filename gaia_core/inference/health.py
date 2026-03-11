"""Health probe interface for GAIA inference backends.

Each backend exposes a probe() method.
The InferRouter calls probe() on a schedule to update circuit breaker state
and report backend availability.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Protocol

log = logging.getLogger(__name__)


@dataclass
class HealthResult:
    backend: str
    available: bool
    latency_ms: float
    detail: str = ""


class HealthProbable(Protocol):
    """Protocol any backend can implement to expose a health probe."""
    def probe(self) -> HealthResult: ...


class LlamaCppHealthProbe:
    """Health probe for the llama.cpp backend."""

    def __init__(self, backend: object) -> None:
        self._backend = backend

    def probe(self) -> HealthResult:
        from gaia_core.inference.contracts import InferBackend, InferRequest
        t0 = time.monotonic()
        try:
            req = InferRequest(
                prompt="ping",
                model_id="health-probe",
                backend=InferBackend.LLAMA_CPP,
                max_tokens=1,
                temperature=0.0,
            )
            self._backend.infer(req)  # type: ignore[union-attr]
            latency_ms = (time.monotonic() - t0) * 1000
            return HealthResult(backend="llama_cpp", available=True, latency_ms=latency_ms)
        except Exception as exc:
            latency_ms = (time.monotonic() - t0) * 1000
            return HealthResult(backend="llama_cpp", available=False, latency_ms=latency_ms, detail=str(exc))


class VLLMHealthProbe:
    """Health probe for the vLLM backend (uses /health HTTP endpoint)."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self._url = base_url.rstrip("/") + "/health"

    def probe(self) -> HealthResult:
        t0 = time.monotonic()
        try:
            import urllib.request
            with urllib.request.urlopen(self._url, timeout=3) as resp:  # noqa: S310
                available = resp.status == 200
            latency_ms = (time.monotonic() - t0) * 1000
            return HealthResult(backend="vllm", available=available, latency_ms=latency_ms)
        except Exception as exc:
            latency_ms = (time.monotonic() - t0) * 1000
            return HealthResult(backend="vllm", available=False, latency_ms=latency_ms, detail=str(exc))


class TritonHealthProbe:
    """Health probe for the Triton Inference Server backend."""

    def __init__(self, url: str = "localhost:8000") -> None:
        self._url = url

    def probe(self) -> HealthResult:
        t0 = time.monotonic()
        try:
            import urllib.request
            health_url = f"http://{self._url}/v2/health/ready"
            with urllib.request.urlopen(health_url, timeout=3) as resp:  # noqa: S310
                available = resp.status == 200
            latency_ms = (time.monotonic() - t0) * 1000
            return HealthResult(backend="triton", available=available, latency_ms=latency_ms)
        except Exception as exc:
            latency_ms = (time.monotonic() - t0) * 1000
            return HealthResult(backend="triton", available=False, latency_ms=latency_ms, detail=str(exc))
