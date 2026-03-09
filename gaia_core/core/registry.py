from __future__ import annotations

from typing import Dict, Iterable

from gaia_core.core.base import BaseCore
from gaia_core.models import CoreName


class CoreRegistry:
    def __init__(self) -> None:
        self._cores: Dict[CoreName, BaseCore] = {}

    def register(self, core: BaseCore) -> None:
        if core.name in self._cores:
            raise ValueError(f"core already registered: {core.name}")
        self._cores[core.name] = core

    def get(self, name: CoreName) -> BaseCore:
        return self._cores[name]

    def all(self) -> Iterable[BaseCore]:
        return self._cores.values()

    def names(self) -> list[str]:
        return [core.name.value for core in self._cores.values()]
