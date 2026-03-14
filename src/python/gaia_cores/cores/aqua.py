from __future__ import annotations

from ..simple_core import SimpleGaiaCore


class AquaCore(SimpleGaiaCore):
    def __init__(self) -> None:
        super().__init__(
            core_id="AQUA",
            domain="fluid systems",
            summary="Fluid systems, hydrology, and ocean-state modeling",
        )
