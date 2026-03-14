"""Model Profile Registry.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §3, §4

ModelProfile is defined in gaia_ai.models and imported here.
The registry is constructor-injected: pass an iterable of ModelProfile
instances at creation time, or use the from_yaml() classmethod to load
from a YAML file.

YAML schema (profiles key):
  profiles:
    - name: llama3-8b-fast
      backend: llama.cpp
      family: llama3
      locality: local
      min_vram_gb: 6
      tags: [fast]
    - ...
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

import yaml

from .models import ModelProfile

log = logging.getLogger(__name__)

__all__ = [
    "ModelProfile",
    "ModelProfileRegistry",
]


class ModelProfileRegistry:
    """Immutable-at-construction registry of ModelProfile instances.

    Keyed by profile.name. Use filter() for multi-criteria queries.
    """

    def __init__(self, profiles: Iterable[ModelProfile]) -> None:
        self._profiles: dict[str, ModelProfile] = {
            profile.name: profile for profile in profiles
        }

    # ------------------------------------------------------------------ #
    # Construction                                                         #
    # ------------------------------------------------------------------ #

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ModelProfileRegistry":
        """Load and construct a registry from a YAML file.

        The YAML file must have a top-level 'profiles' key containing
        a list of objects whose fields match ModelProfile.
        """
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        profiles = [ModelProfile(**item) for item in data.get("profiles", [])]
        log.debug("registry: loaded %d profile(s) from '%s'", len(profiles), path)
        return cls(profiles)

    # ------------------------------------------------------------------ #
    # Lookup                                                               #
    # ------------------------------------------------------------------ #

    def get(self, name: str) -> ModelProfile:
        """Return a profile by name; raises KeyError if not found."""
        return self._profiles[name]

    def all(self) -> list[ModelProfile]:
        """Return all registered profiles.

        Used by InferenceRouter.decide().
        """
        return list(self._profiles.values())

    # ------------------------------------------------------------------ #
    # Filtering                                                            #
    # ------------------------------------------------------------------ #

    def filter(
        self,
        *,
        locality: str | None = None,
        supports_embeddings: bool | None = None,
        supports_tool_use: bool | None = None,
        tag: str | None = None,
        trust_tier: str | None = None,
    ) -> list[ModelProfile]:
        """Return profiles matching ALL provided criteria.

        All parameters are optional keyword-only. Passing no arguments
        is equivalent to calling all().
        """
        results = self.all()
        if locality is not None:
            results = [p for p in results if p.locality == locality]
        if supports_embeddings is not None:
            results = [p for p in results if p.supports_embeddings is supports_embeddings]
        if supports_tool_use is not None:
            results = [p for p in results if p.supports_tool_use is supports_tool_use]
        if tag is not None:
            results = [p for p in results if tag in p.tags]
        if trust_tier is not None:
            results = [p for p in results if p.trust_tier == trust_tier]
        return results

    # ------------------------------------------------------------------ #
    # Metadata                                                             #
    # ------------------------------------------------------------------ #

    @property
    def model_names(self) -> tuple[str, ...]:
        return tuple(self._profiles.keys())

    def __len__(self) -> int:
        return len(self._profiles)

    def __repr__(self) -> str:
        return f"ModelProfileRegistry({list(self._profiles.keys())})"
