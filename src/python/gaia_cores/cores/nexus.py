from __future__ import annotations

from ..simple_core import SimpleGaiaCore


class NexusCore(SimpleGaiaCore):
    def __init__(self) -> None:
        super().__init__(
            core_id="NEXUS",
            domain="coordination",
            summary="Cross-core federation, coordination, and synchronization",
        )

    @property
    def protection_class(self) -> str:
        return "critical"
