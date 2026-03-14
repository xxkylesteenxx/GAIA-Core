from __future__ import annotations

from ..simple_core import SimpleGaiaCore


class VitaCore(SimpleGaiaCore):
    def __init__(self) -> None:
        super().__init__(
            core_id="VITA",
            domain="biosystems",
            summary="Biological systems, health, and life monitoring",
        )
