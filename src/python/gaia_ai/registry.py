"""Model Profile Registry.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §3, §4

ModelProfile is now defined in gaia_ai.models and re-exported here
for backward compat. The registry stores and queries ModelProfile
instances; callers may import ModelProfile from either module.

Legacy types (Locality, HardwareMinima, RegistryModelProfile) are kept
for code that predates the flat ModelProfile schema.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .models import ModelProfile

log = logging.getLogger(__name__)

# Re-export so existing `from .registry import ModelProfile` still works.
__all__ = [
    "HardwareMinima",
    "Locality",
    "ModelProfile",
    "ModelProfileRegistry",
]


# ---------------------------------------------------------------------------
# Legacy locality / hardware types (kept for backward compat)
# ---------------------------------------------------------------------------

class Locality(str, Enum):
    LOCAL_FAST      = "local_fast"
    LOCAL_EMBEDDING = "local_embedding"
    LOCAL_DEEP      = "local_deep"
    CLOUD           = "cloud"


@dataclass
class HardwareMinima:
    ram_gb:    float = 0.0
    vram_gb:   float = 0.0
    cpu_cores: int   = 1


# ---------------------------------------------------------------------------
# ModelProfileRegistry
# ---------------------------------------------------------------------------

class ModelProfileRegistry:
    """Register, approve, and query ModelProfile instances.

    Profiles are now flat ModelProfile (from models.py). The registry
    uses profile.name as the key.

    External / cloud routes should be tracked via trust_tier and tags;
    the deny-by-default approval gate from the old schema is represented
    by trust_tier == 'external' + the caller checking before use.
    """

    def __init__(self) -> None:
        self._profiles: dict[str, ModelProfile] = {}

    def register(self, profile: ModelProfile) -> None:
        if profile.name in self._profiles:
            raise ValueError(f"model already registered: {profile.name}")
        if profile.locality == "cloud" or profile.trust_tier == "external":
            log.warning(
                "registry: external model '%s' registered (trust_tier=%s) — "
                "verify approval before routing",
                profile.name, profile.trust_tier,
            )
        self._profiles[profile.name] = profile
        log.debug("registry: registered model '%s' [%s]",
                  profile.name, profile.locality)

    def get(self, name: str) -> ModelProfile:
        return self._profiles[name]

    def all(self) -> list[ModelProfile]:
        """Return all registered profiles.

        Used by InferenceRouter.decide().
        """
        return list(self._profiles.values())

    def all_local(self) -> list[ModelProfile]:
        """Return profiles whose locality is not 'cloud'."""
        return [p for p in self._profiles.values() if p.locality != "cloud"]

    def by_tag(self, tag: str) -> list[ModelProfile]:
        return [p for p in self._profiles.values() if tag in p.tags]

    def by_locality(self, locality: str) -> list[ModelProfile]:
        return [p for p in self._profiles.values() if p.locality == locality]

    def from_yaml(self, path: str) -> "ModelProfileRegistry":
        """Load and register profiles from a YAML file.

        Requires: pyyaml
        See gaia_ai/README.md for the expected YAML schema.
        """
        import yaml  # type: ignore[import]
        with open(path) as f:
            data = yaml.safe_load(f)
        for entry in data.get("models", []):
            tags = entry.pop("tags", [])
            self.register(ModelProfile(tags=tags, **entry))
        return self

    @property
    def model_names(self) -> tuple[str, ...]:
        return tuple(self._profiles.keys())

    # Backward-compat alias
    @property
    def model_ids(self) -> tuple[str, ...]:
        return self.model_names
