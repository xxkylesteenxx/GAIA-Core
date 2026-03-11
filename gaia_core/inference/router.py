"""Policy-based inference router with health probes and circuit breakers.

Routing priority:
  1. Explicit backend in InferRequest.backend
  2. model_profile_registry.yaml lookup
  3. Fallback: llama_cpp (always available offline)

Circuit breaker opens after 3 consecutive failures per backend.
Health probes can be triggered manually or on a schedule.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None  # type: ignore

from gaia_core.inference.circuit_breaker import CircuitBreaker, CircuitBreakerConfig
from gaia_core.inference.contracts import InferBackend, InferRequest, InferResponse
from gaia_core.inference.health import HealthResult

log = logging.getLogger(__name__)

_REGISTRY_PATH = Path(__file__).parent.parent.parent / "model_profile_registry.yaml"


def _load_registry() -> dict:
    if yaml is None or not _REGISTRY_PATH.exists():
        return {}
    with _REGISTRY_PATH.open() as fh:
        return yaml.safe_load(fh) or {}


def _resolve_backend(request: InferRequest) -> InferBackend:
    if request.backend is not None:
        return request.backend
    registry = _load_registry()
    profile = registry.get("models", {}).get(request.model_id, {})
    backend_str = profile.get("backend", InferBackend.LLAMA_CPP.value)
    try:
        return InferBackend(backend_str)
    except ValueError:
        log.warning(
            "Unknown backend '%s' for model '%s', falling back to llama_cpp",
            backend_str, request.model_id,
        )
        return InferBackend.LLAMA_CPP


class InferRouter:
    """Routes InferRequests to the correct backend with circuit breaker protection."""

    def __init__(self, cb_config: CircuitBreakerConfig | None = None) -> None:
        self._backends: dict[InferBackend, Any] = {}
        self._probes: dict[InferBackend, Any] = {}
        self._breakers: dict[InferBackend, CircuitBreaker] = {}
        self._cb_config = cb_config or CircuitBreakerConfig()

    def register(
        self,
        backend: InferBackend,
        impl: Any,
        probe: Any = None,
    ) -> None:
        """Register a backend implementation and optional health probe."""
        self._backends[backend] = impl
        self._breakers[backend] = CircuitBreaker(
            name=backend.value,
            config=self._cb_config,
        )
        if probe is not None:
            self._probes[backend] = probe
        log.info("Registered inference backend: %s", backend.value)

    def infer(self, request: InferRequest) -> InferResponse:
        """Route request through circuit breaker to the resolved backend."""
        backend_key = _resolve_backend(request)
        impl = self._backends.get(backend_key)
        if impl is None:
            raise RuntimeError(
                f"No backend registered for {backend_key}. "
                "Register one via InferRouter.register()."
            )
        breaker = self._breakers[backend_key]
        return breaker.call(lambda: impl.infer(request))

    def probe(self, backend: InferBackend) -> HealthResult | None:
        """Run health probe for a specific backend and update circuit breaker."""
        probe_impl = self._probes.get(backend)
        if probe_impl is None:
            log.debug("No health probe registered for %s", backend.value)
            return None
        result = probe_impl.probe()
        breaker = self._breakers.get(backend)
        if breaker:
            if result.available:
                breaker.record_success()
            else:
                breaker.record_failure()
                log.warning(
                    "Health probe FAILED for %s: %s", backend.value, result.detail
                )
        return result

    def probe_all(self) -> dict[str, HealthResult]:
        """Run health probes for all registered backends."""
        results = {}
        for backend in self._backends:
            result = self.probe(backend)
            if result is not None:
                results[backend.value] = result
        return results

    def health_summary(self) -> dict[str, Any]:
        """Return circuit breaker status for all backends."""
        return {
            backend.value: self._breakers[backend].status()
            for backend in self._breakers
        }
