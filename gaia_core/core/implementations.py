from __future__ import annotations

from typing import Any, Dict

from gaia_core.core.base import BaseCore
from gaia_core.models import CoreName


class GenericCore(BaseCore):
    def __init__(self, name: CoreName, purpose: str, specialty: str) -> None:
        super().__init__(name=name, purpose=purpose)
        self.specialty = specialty

    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        self.state.last_inputs.append(message)
        kind = message.get("kind", "unknown")
        self.state.last_summary = f"{self.name.value} processed {kind}"
        self.state.metrics["handled_messages"] = (
            self.state.metrics.get("handled_messages", 0.0) + 1.0
        )
        return {
            "core": self.name.value,
            "accepted": True,
            "specialty": self.specialty,
            "kind": kind,
            "summary": self.state.last_summary,
        }


def build_core_set() -> list[GenericCore]:
    return [
        GenericCore(CoreName.NEXUS,    "cross-core coordination and synchronization",  "routing, timing, consensus"),
        GenericCore(CoreName.GUARDIAN, "safety, policy, and actuation boundaries",      "veto, approval, oversight"),
        GenericCore(CoreName.ATLAS,    "planetary grounding and Earth-system intake",   "sensor normalization, source routing"),
        GenericCore(CoreName.SOPHIA,   "wisdom, language, reasoning, uncertainty",      "dialogue, explanation, synthesis"),
        GenericCore(CoreName.TERRA,    "terrestrial and geophysical intelligence",      "land, soil, wildfire, seismic"),
        GenericCore(CoreName.AQUA,     "hydrological and ocean intelligence",           "rivers, watersheds, oceans"),
        GenericCore(CoreName.AERO,     "atmospheric and climate intelligence",          "air, weather, climate"),
        GenericCore(CoreName.VITA,     "biosphere and ecological intelligence",         "species, habitats, biodiversity"),
    ]
