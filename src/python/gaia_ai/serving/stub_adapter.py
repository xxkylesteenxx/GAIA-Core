"""Deterministic stub adapter for tests and demos."""

from __future__ import annotations

from typing import Any

from .base import ServingAdapter


class StubAdapter(ServingAdapter):
    """Returns a predictable response. No network required."""

    def __init__(self, response: str = "[STUB]") -> None:
        self.response    = response
        self._call_count = 0

    async def infer(self, prompt: str, *, max_tokens: int = 512, **kwargs: Any) -> str:
        self._call_count += 1
        return f"{self.response} prompt={prompt[:40]!r}"

    async def health(self) -> bool:
        return True

    @property
    def call_count(self) -> int:
        return self._call_count
