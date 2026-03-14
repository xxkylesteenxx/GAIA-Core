"""Inference Router.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §3, §4, §5

The router selects among local_fast, local_embedding, and cloud_deep
profiles based on latency, privacy, and task mode.

Private-data requests SHALL prefer approved local routes when available.
External model routes SHALL be deny-by-default unless registered and approved.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .registry import Locality, ModelProfile, ModelProfileRegistry
from .serving import ServingAdapter

log = logging.getLogger(__name__)


class TaskMode(str, Enum):
    CHAT          = "chat"
    COMPLETION    = "completion"
    EMBEDDING     = "embedding"
    CLASSIFICATION = "classification"
    SUMMARISATION = "summarisation"
    CODE          = "code"


@dataclass
class InferenceRequest:
    prompt:       str
    task_mode:    TaskMode          = TaskMode.CHAT
    private_data: bool              = False
    preferred_model: str | None     = None
    max_tokens:   int               = 512
    metadata:     dict[str, Any]    = field(default_factory=dict)


@dataclass
class InferenceResponse:
    model_id:  str
    locality:  str
    content:   str
    metadata:  dict[str, Any]       = field(default_factory=dict)
    truncated: bool                 = False


class RoutingError(Exception):
    """Raised when no suitable route is available."""


class InferenceRouter:
    """Select a model profile and dispatch an inference request.

    Routing priority (highest to lowest):
      1. Caller-specified preferred_model (if approved and available)
      2. Local route matching task_mode capability tag
      3. Any approved local route
      4. Cloud route (only if private_data=False and route is approved)

    Raises RoutingError if no route satisfies constraints.
    """

    def __init__(
        self,
        registry: ModelProfileRegistry,
        adapters: dict[str, ServingAdapter] | None = None,
    ) -> None:
        self._registry = registry
        self._adapters: dict[str, ServingAdapter] = adapters or {}

    def bind_adapter(self, model_id: str, adapter: ServingAdapter) -> None:
        """Attach a serving adapter to a registered model."""
        self._adapters[model_id] = adapter

    def select(self, request: InferenceRequest) -> ModelProfile:
        """Return the best ModelProfile for request without executing it."""
        # 1. Explicit preference
        if request.preferred_model:
            profile = self._registry.get(request.preferred_model)
            self._assert_routable(profile, request)
            return profile

        candidates = self._registry.all_approved()

        # 2. Private-data: filter to local only
        if request.private_data:
            candidates = [p for p in candidates if p.is_private_safe()]
            if not candidates:
                raise RoutingError(
                    "No approved local route available for private-data request"
                )

        # 3. Prefer capability-tagged match for task_mode
        task_tag = request.task_mode.value
        tagged = [p for p in candidates if p.has_capability(task_tag)]
        if tagged:
            return tagged[0]

        # 4. Prefer local over cloud
        local = [p for p in candidates if p.is_private_safe()]
        if local:
            return local[0]

        # 5. Cloud fallback (private_data already excluded above)
        cloud = [p for p in candidates if not p.is_private_safe()]
        if cloud:
            return cloud[0]

        raise RoutingError("No routable model profile found")

    async def route(self, request: InferenceRequest) -> InferenceResponse:
        """Select a profile and dispatch via its bound serving adapter."""
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
            raise RoutingError(
                f"External model '{profile.model_id}' is not approved"
            )
        if request.private_data and not profile.is_private_safe():
            raise RoutingError(
                f"Model '{profile.model_id}' is a cloud route and cannot handle private data"
            )
