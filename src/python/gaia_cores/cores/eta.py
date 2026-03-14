from __future__ import annotations

from ..simple_core import SimpleGaiaCore


class EtaCore(SimpleGaiaCore):
    def __init__(self) -> None:
        super().__init__(
            core_id="ETA",
            domain="temporal",
            summary="Temporal coordination, event sequencing, and scheduling",
        )
