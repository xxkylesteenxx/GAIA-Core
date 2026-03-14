from __future__ import annotations

from ..simple_core import SimpleGaiaCore


class AeroCore(SimpleGaiaCore):
    def __init__(self) -> None:
        super().__init__(
            core_id="AERO",
            domain="atmosphere",
            summary="Atmospheric state, weather, and air-quality interpretation",
        )
