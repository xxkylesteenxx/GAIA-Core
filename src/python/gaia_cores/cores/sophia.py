from __future__ import annotations

from ..simple_core import SimpleGaiaCore


class SophiaCore(SimpleGaiaCore):
    def __init__(self) -> None:
        super().__init__(
            core_id="SOPHIA",
            domain="policy",
            summary="Policy reasoning, ethics arbitration, and coordination hub",
        )

    @property
    def protection_class(self) -> str:
        return "critical"
