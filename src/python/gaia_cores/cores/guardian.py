from __future__ import annotations

from ..simple_core import SimpleGaiaCore


class GuardianCore(SimpleGaiaCore):
    def __init__(self) -> None:
        super().__init__(
            core_id="GUARDIAN",
            domain="safety and ethics",
            summary="Safety, ethics, and harm-prevention supervision",
        )

    @property
    def protection_class(self) -> str:
        return "critical"
