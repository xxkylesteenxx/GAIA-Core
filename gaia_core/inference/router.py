"""Policy-based inference router.

Routing priority:
  1. Explicit backend in InferRequest.backend
  2. model_profile_registry.yaml lookup
  3. Fallback: llama_cpp (always available offline)
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

from gaia_core.inference.contracts import InferBackend, InferRequest, InferResponse

if TYPE_CHECKING:
    pass

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
        log.warning("Unknown backend '%s' for model '%s', falling back to llama_cpp", backend_str, request.model_id)
        return InferBackend.LLAMA_CPP


class InferRouter:
    """Routes InferRequests to the correct backend."""

    def __init__(self) -> None:
        self._backends: dict[InferBackend, object] = {}

    def register(self, backend: InferBackend, impl: object) -> None:
        self._backends[backend] = impl

    def infer(self, request: InferRequest) -> InferResponse:
        backend_key = _resolve_backend(request)
        impl = self._backends.get(backend_key)
        if impl is None:
            raise RuntimeError(f"No backend registered for {backend_key}. Register one via InferRouter.register().")
        return impl.infer(request)  # type: ignore[union-attr]
