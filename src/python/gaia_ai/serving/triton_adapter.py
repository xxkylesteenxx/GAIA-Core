"""Triton Inference Server adapter placeholder.

Replace stub body with tritonclient.grpc.aio calls for production.
Requires: pip install gaia-python[triton]
"""

from __future__ import annotations

import logging
from typing import Any

from .base import ServingAdapter

log = logging.getLogger(__name__)


class TritonAdapter(ServingAdapter):
    def __init__(
        self,
        base_url:   str = "http://localhost:8001",
        model_name: str = "gaia_model",
    ) -> None:
        self.base_url   = base_url
        self.model_name = model_name
        log.warning(
            "TritonAdapter: stub active — replace with tritonclient.grpc.aio for production"
        )

    async def infer(self, prompt: str, *, max_tokens: int = 512, **kwargs: Any) -> str:
        # TODO: tritonclient.grpc.aio inference call
        return f"[TRITON-STUB] {prompt[:80]}"

    async def health(self) -> bool:
        # TODO: GET /v2/health/ready
        return False
