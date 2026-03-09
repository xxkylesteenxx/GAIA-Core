from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List

from gaia_core.models import CoreName


@dataclass(slots=True)
class CoreState:
    core: CoreName
    active: bool = True
    last_summary: str = "idle"
    working_memory: Dict[str, Any] = field(default_factory=dict)
    last_inputs: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)


class BaseCore(ABC):
    def __init__(self, name: CoreName, purpose: str):
        self.name = name
        self.purpose = purpose
        self.state = CoreState(core=name)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "name": self.name.value,
            "purpose": self.purpose,
            "active": self.state.active,
            "last_summary": self.state.last_summary,
            "metrics": dict(self.state.metrics),
        }

    @abstractmethod
    def handle(self, message: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

    def tick(self) -> Dict[str, Any]:
        return {
            "core": self.name.value,
            "status": "ok",
            "summary": self.state.last_summary,
        }
