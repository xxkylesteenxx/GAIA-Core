"""GAIA Python orchestration demo.

Boots all eight cores, broadcasts a planetary state update,
sends a policy-check message from NEXUS to GUARDIAN, and
prints the health table and state snapshots.

Usage:
    cd src/python
    python examples/run_demo.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from pprint import pprint

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from gaia_cores.cores import (
    AeroCore,
    AquaCore,
    EtaCore,
    GuardianCore,
    NexusCore,
    SophiaCore,
    TerraCore,
    VitaCore,
)
from gaia_cores.models import GaiaMessage, StateUpdate
from gaia_cores.propagation import StatePropagator
from gaia_cores.registry import CoreRegistry


async def main() -> None:
    registry = CoreRegistry()
    cores = [
        TerraCore(), AquaCore(), AeroCore(), VitaCore(),
        SophiaCore(), GuardianCore(), NexusCore(), EtaCore(),
    ]
    await registry.register_many(cores)
    await registry.boot_all()

    propagator = StatePropagator(registry)
    await propagator.broadcast(
        StateUpdate(
            source="planetary_ingest",
            scope="global",
            values={"temperature_anomaly_c": 1.29, "ocean_heat_content": "elevated"},
            summary="Planetary baseline state loaded",
        )
    )

    await registry.send(
        GaiaMessage(
            sender="NEXUS",
            recipient="GUARDIAN",
            topic="policy_check",
            payload={"operation": "synchronize_global_state", "risk_tier": "medium"},
        )
    )

    health = await registry.health_table()
    print("== health ==")
    pprint({k: v.status.value for k, v in health.items()})

    print("\n== snapshots ==")
    snapshots = registry.snapshot_all()
    pprint({k: v.values for k, v in snapshots.items()})

    await registry.stop_all()
    print("\n[gaia] shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
