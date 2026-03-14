"""OpenAI-compatible serving adapter.

Suitable for:
  - vLLM local serving  (vllm serve <model> --api-key none)
  - LM Studio, llama.cpp server, and other OpenAI-API-compatible servers
  - OpenAI cloud API (requires approved external route in registry)

Requires: pip install gaia-python[openai]
"""

from __future__ import annotations

import logging
from typing import Any

from .base import ServingAdapter

log = logging.getLogger(__name__)


class OpenAIAdapter(ServingAdapter):
    def __init__(
        self,
        base_url: str   = "http://localhost:8000/v1",
        api_key:  str   = "none",
        model:    str   = "default",
        timeout:  float = 30.0,
    ) -> None:
        self.base_url = base_url
        self.api_key  = api_key
        self.model    = model
        self.timeout  = timeout

    async def infer(self, prompt: str, *, max_tokens: int = 512, **kwargs: Any) -> str:
        try:
            from openai import AsyncOpenAI  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "openai package required: pip install 'gaia-python[openai]'"
            ) from exc
        client   = AsyncOpenAI(base_url=self.base_url, api_key=self.api_key)
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
