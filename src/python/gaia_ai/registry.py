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
    """
    model_id:        str
    locality:        Locality
    context_window:  int
    capability_tags: list[str]           = field(default_factory=list)
    hardware_minima: HardwareMinima      = field(default_factory=HardwareMinima)
    approved:        bool                = False   # external routes deny-by-default
    endpoint:        str                 = ""      # serving endpoint URL or path
    metadata:        dict[str, Any]      = field(default_factory=dict)

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
        log.debug("registry: registered model '%s' [%s]", profile.model_id, profile.locality.value)

    def approve(self, model_id: str) -> None:
        """Explicitly approve an external (cloud) route."""
        profile = self._profiles.get(model_id)
        if profile is None:
            raise KeyError(f"unknown model: {model_id}")
        profile.approved = True
        log.info("registry: approved external route '%s'", model_id)

    def get(self, model_id: str) -> ModelProfile:
        return self._profiles[model_id]

    def all_approved(self) -> list[ModelProfile]:
        return [p for p in self._profiles.values() if p.approved or p.is_private_safe()]

    def by_locality(self, locality: Locality) -> list[ModelProfile]:
        return [p for p in self._profiles.values() if p.locality == locality]

    def by_capability(self, tag: str) -> list[ModelProfile]:
        return [p for p in self._profiles.values() if p.has_capability(tag)]

    @property
    def model_ids(self) -> tuple[str, ...]:
        return tuple(self._profiles.keys())
