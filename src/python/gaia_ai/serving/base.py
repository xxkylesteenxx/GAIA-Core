"""ServingAdapter abstract base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ServingAdapter(ABC):
    """Abstract base for all GAIA serving backends."""

    @abstractmethod
    async def infer(self, prompt: str, *, max_tokens: int = 512, **kwargs: Any) -> str:
        """Run inference and return generated text."""

    @abstractmethod
    async def health(self) -> bool:
        """Return True if the backend is reachable and ready."""
