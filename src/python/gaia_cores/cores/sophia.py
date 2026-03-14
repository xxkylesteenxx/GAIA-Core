from __future__ import annotations

from ..simple_core import SimpleGaiaCore


class SophiaCore(SimpleGaiaCore):
    def __init__(self) -> None:
        super().__init__(
            core_id="SOPHIA",
            domain="knowledge synthesis",
            summary="Knowledge synthesis, reflection, and higher-order integration",
        )

    @property
    def protection_class(self) -> str:
        return "critical"
