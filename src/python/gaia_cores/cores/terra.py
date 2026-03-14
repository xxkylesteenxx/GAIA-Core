from __future__ import annotations

from ..simple_core import SimpleGaiaCore


class TerraCore(SimpleGaiaCore):
    def __init__(self) -> None:
        super().__init__(
            core_id="TERRA",
            domain="earth-system sensing",
            summary="Earth-system sensing and environmental data ingestion",
        )
