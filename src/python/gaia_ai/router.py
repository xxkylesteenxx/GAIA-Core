"""Inference Router.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §3, §4, §5

Two router classes are provided:

  InferenceRouter       —  canonical policy router (spec-primary)
                           Sync. Uses InferenceMode + QueryContext + RouteDecision
                           from gaia_ai.models. Returns a RouteDecision— the caller
                           dispatches via a serving adapter.

  InferenceRouterAsync  —  async variant that owns serving adapters and dispatches
                           directly. Kept for backward compat with existing tests
                           and async demo pipeline.

Routing policy (InferenceRouter.decide)
---------------------------------------
  1. Embedding mode  →  supports_embeddings profile, local://embeddings
  2. Private data    →  local non-embedding profile, retrieval + guard required
  3. Fast / low latency (≤ 1200 ms budget)  →  "fast" tag, local
  4. Default deep    →  "deep" tag, approved cloud

Spec invariants
---------------
  - Private-data requests SHALL prefer approved local routes.
  - External routes SHALL be deny-by-default unless registered and approved.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .models import InferenceMode, QueryContext, RouteDecision
from .registry import Locality, ModelProfile, ModelProfileRegistry
from .serving.base import ServingAdapter

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# InferenceRouter  —  canonical sync policy router (spec-primary)
# ---------------------------------------------------------------------------

class InferenceRouter:
    """Policy router for local/cloud and fast/deep selection.

    Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §4
    """

    def __init__(self, registry: ModelProfileRegistry) -> None:
        self.registry = registry

    def decide(self, query: QueryContext) -> RouteDecision:
        profiles = self.registry.all()

        if query.mode == InferenceMode.EMBEDDING:
            candidate = next(
                (p for p in profiles if p.supports_embeddings), None
            )
            if candidate is None:
                raise RoutingError("No embedding-capable profile registered")
            return RouteDecision(
                profile=candidate,
                endpoint="local://embeddings",
                reason="Embedding request routed to local embedding-capable profile.",
                retrieval_required=False,
                guard_scan_required=False,
            )

        if query.requires_private_data:
            local_candidates = [
                p for p in profiles
                if p.locality != Locality.CLOUD and not p.supports_embeddings
            ]
            if not local_candidates:
                raise RoutingError(
                    "No approved local route available for private-data request"
                )
            candidate = local_candidates[0]
            return RouteDecision(
                profile=candidate,
                endpoint=candidate.endpoint or "http://127.0.0.1:8000/v1",
                reason="Private-data request kept local.",
                retrieval_required=True,
                guard_scan_required=True,
            )

        if query.latency_budget_ms <= 1200 or query.mode == InferenceMode.FAST:
            fast_local = next(
                (p for p in profiles if "fast" in p.tags), None
            )
            if fast_local is None:
                raise RoutingError("No fast-tagged profile registered")
            return RouteDecision(
                profile=fast_local,
                endpoint=fast_local.endpoint or "http://127.0.0.1:8000/v1",
                reason="Low-latency route selected.",
                retrieval_required=False,
                guard_scan_required=True,
            )

        deep = next(
            (p for p in profiles if "deep" in p.tags and p.approved), None
        )
        if deep is None:
            raise RoutingError(
                "No approved deep profile registered. "
                "Call registry.approve(<model_id>) to enable cloud/deep routes."
            )
        return RouteDecision(
            profile=deep,
            endpoint=deep.endpoint or "https://approved-cloud.example/v1",
            reason="High-depth route selected.",
            retrieval_required=True,
            guard_scan_required=True,
        )


# ---------------------------------------------------------------------------
# RoutingError
# ---------------------------------------------------------------------------

class RoutingError(Exception):
    """Raised when no suitable route is available."""


# ---------------------------------------------------------------------------
# InferenceRouterAsync  —  async variant (backward compat)
# ---------------------------------------------------------------------------

# Legacy types kept for backward compat with existing tests and demo pipeline.

class TaskMode(str, Enum):
    CHAT           = "chat"
    COMPLETION     = "completion"
    EMBEDDING      = "embedding"
    CLASSIFICATION = "classification"
    SUMMARISATION  = "summarisation"
    CODE           = "code"


@dataclass
class InferenceRequest:
    prompt:          str
    task_mode:       TaskMode        = TaskMode.CHAT
    private_data:    bool            = False
    preferred_model: str | None      = None
    max_tokens:      int             = 512
    metadata:        dict[str, Any]  = field(default_factory=dict)


@dataclass
class InferenceResponse:
    model_id:  str
    locality:  str
    content:   str
    metadata:  dict[str, Any] = field(default_factory=dict)
    truncated: bool           = False


class InferenceRouterAsync:
    """Async router that owns serving adapters and dispatches directly.

    Kept for backward compat with existing tests and async demo pipeline.
    For new code, prefer InferenceRouter (sync) + explicit adapter dispatch.
    """

    def __init__(
        self,
        registry: ModelProfileRegistry,
        adapters: dict[str, ServingAdapter] | None = None,
    ) -> None:
        self._registry = registry
        self._adapters: dict[str, ServingAdapter] = adapters or {}

    def bind_adapter(self, model_id: str, adapter: ServingAdapter) -> None:
        self._adapters[model_id] = adapter

    def select(self, request: InferenceRequest) -> ModelProfile:
        if request.preferred_model:
            profile = self._registry.get(request.preferred_model)
            self._assert_routable(profile, request)
            return profile

        candidates = self._registry.all_approved()

        if request.private_data:
            candidates = [p for p in candidates if p.is_private_safe()]
            if not candidates:
                raise RoutingError(
                    "No approved local route available for private-data request"
                )

        task_tag = request.task_mode.value
        tagged = [p for p in candidates if p.has_capability(task_tag)]
        if tagged:
            return tagged[0]

        local = [p for p in candidates if p.is_private_safe()]
        if local:
            return local[0]

        cloud = [p for p in candidates if not p.is_private_safe()]
        if cloud:
            return cloud[0]

        raise RoutingError("No routable model profile found")

    async def route(self, request: InferenceRequest) -> InferenceResponse:
        profile = self.select(request)
        adapter = self._adapters.get(profile.model_id)
        if adapter is None:
            raise RoutingError(
                f"No serving adapter bound for model '{profile.model_id}'"
            )
        log.info(
            "router: dispatching '%s' via %s [%s]",
            request.task_mode.value, profile.model_id, profile.locality.value,
        )
        content = await adapter.infer(request.prompt, max_tokens=request.max_tokens)
        return InferenceResponse(
            model_id=profile.model_id,
            locality=profile.locality.value,
            content=content,
        )

    @staticmethod
    def _assert_routable(profile: ModelProfile, request: InferenceRequest) -> None:
        if not profile.approved and not profile.is_private_safe():
            raise RoutingError(f"External model '{profile.model_id}' is not approved")
        if request.private_data and not profile.is_private_safe():
            raise RoutingError(
                f"Model '{profile.model_id}' is a cloud route and cannot handle private data"
            )
