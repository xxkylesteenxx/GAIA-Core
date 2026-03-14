from __future__ import annotations

from ..simple_core import SimpleGaiaCore


class AquaCore(SimpleGaiaCore):
    def __init__(self) -> None:
        super().__init__(
            core_id="AQUA",
            domain="hydrology",
            summary="Hydrological cycles, ocean state, and freshwater systems",
        )
