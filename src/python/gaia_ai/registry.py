"""Model Profile Registry.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §3, §4

Model profiles SHALL declare locality, hardware minima,
context windows, and capability tags.
External model routes SHALL be deny-by-default unless
registered and approved.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

log = logging.getLogger(__name__)


class Locality(str, Enum):
    LOCAL_FAST      = "local_fast"       # small, on-device, low latency
    LOCAL_EMBEDDING = "local_embedding"  # embedding-specialised local model
    LOCAL_DEEP      = "local_deep"       # large local model, high compute
    CLOUD           = "cloud"            # external route; deny-by-default


@dataclass
class HardwareMinima:
    ram_gb:    float = 0.0
    vram_gb:   float = 0.0
    cpu_cores: int   = 1


@dataclass
class ModelProfile:
    """Declares everything needed to route, bind, and govern a model.

    Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §4

    The `tags` field is the canonical router-facing tag list used by
    InferenceRouter.decide() for fast/deep/embedding routing.
    It is derived from `capability_tags` if not provided explicitly.
    """
    model_id:           str
    locality:           Locality
    context_window:     int
    capability_tags:    list[str]       = field(default_factory=list)
    hardware_minima:    HardwareMinima  = field(default_factory=HardwareMinima)
    approved:           bool            = False   # external routes deny-by-default
    endpoint:           str             = ""      # serving endpoint URL or path
    supports_embeddings: bool           = False   # True for embedding-specialised models
    metadata:           dict[str, Any]  = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Auto-set supports_embeddings for LOCAL_EMBEDDING locality
        if self.locality == Locality.LOCAL_EMBEDDING:
            self.supports_embeddings = True

    @property
    def tags(self) -> list[str]:
        """Router-facing tag list.

        Includes capability_tags plus synthetic locality tags
        ('fast', 'deep', 'embedding') so InferenceRouter.decide()
        can query `'fast' in p.tags` without requiring callers to
        declare those tags explicitly.
        """
        base = list(self.capability_tags)
        if self.locality == Locality.LOCAL_FAST and "fast" not in base:
            base.append("fast")
        if self.locality == Locality.LOCAL_DEEP and "deep" not in base:
            base.append("deep")
        if self.supports_embeddings and "embedding" not in base:
            base.append("embedding")
        return base

    def is_private_safe(self) -> bool:
        """True if this route is safe for private-data requests."""
        return self.locality != Locality.CLOUD

    def has_capability(self, tag: str) -> bool:
        return tag in self.capability_tags


class ModelProfileRegistry:
    """Register, approve, and query ModelProfile instances.

    External routes are deny-by-default: they must be explicitly
    approved via approve() before the router will select them.
    """

    def __init__(self) -> None:
        self._profiles: dict[str, ModelProfile] = {}

    def register(self, profile: ModelProfile) -> None:
        if profile.model_id in self._profiles:
            raise ValueError(f"model already registered: {profile.model_id}")
        if profile.locality == Locality.CLOUD and not profile.approved:
            log.warning(
                "registry: external model '%s' registered but not approved — "
                "router will deny until approve() is called",
                profile.model_id,
            )
        self._profiles[profile.model_id] = profile
        log.debug("registry: registered model '%s' [%s]",
                  profile.model_id, profile.locality.value)

    def approve(self, model_id: str) -> None:
        """Explicitly approve an external (cloud) route."""
        profile = self._profiles.get(model_id)
        if profile is None:
            raise KeyError(f"unknown model: {model_id}")
        profile.approved = True
        log.info("registry: approved external route '%s'", model_id)

    def get(self, model_id: str) -> ModelProfile:
        return self._profiles[model_id]

    def all(self) -> list[ModelProfile]:
        """Return all registered profiles (approved and unapproved).

        The router is responsible for filtering by approval state.
        Used by InferenceRouter.decide().
        """
        return list(self._profiles.values())

    def all_approved(self) -> list[ModelProfile]:
        """Return only profiles that are approved or local (private-safe)."""
        return [p for p in self._profiles.values() if p.approved or p.is_private_safe()]

    def by_locality(self, locality: Locality) -> list[ModelProfile]:
        return [p for p in self._profiles.values() if p.locality == locality]

    def by_capability(self, tag: str) -> list[ModelProfile]:
        return [p for p in self._profiles.values() if p.has_capability(tag)]

    def from_yaml(self, path: str) -> "ModelProfileRegistry":
        """Load profiles from a YAML file and register them.

        Requires: pyyaml
        See gaia_ai/README.md for the expected YAML schema.
        """
        import yaml  # type: ignore[import]
        with open(path) as f:
            data = yaml.safe_load(f)
        for entry in data.get("models", []):
            locality_str = entry.pop("locality", "local_fast")
            locality = Locality(locality_str)
            hw_raw = entry.pop("hardware_minima", {})
            hw = HardwareMinima(**hw_raw) if hw_raw else HardwareMinima()
            self.register(ModelProfile(locality=locality, hardware_minima=hw, **entry))
        return self

    @property
    def model_ids(self) -> tuple[str, ...]:
        return tuple(self._profiles.keys())
