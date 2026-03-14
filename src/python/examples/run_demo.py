"""GAIA Python orchestration demo.

Boots all eight cores, sends a test message from TERRA to SOPHIA,
and prints the registry health table and state snapshots.

Usage:
    cd src/python
    python examples/run_demo.py
"""

import asyncio
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gaia_cores.bus import CoreMessageBus
from gaia_cores.models import CoreMessage
from gaia_cores.registry import CoreRegistry
from gaia_cores.cores.terra import TerraCore
from gaia_cores.cores.aqua import AquaCore
from gaia_cores.cores.aero import AeroCore
from gaia_cores.cores.vita import VitaCore
from gaia_cores.cores.sophia import SophiaCore
from gaia_cores.cores.guardian import GuardianCore
from gaia_cores.cores.nexus import NexusCore
from gaia_cores.cores.eta import EtaCore

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


async def main() -> None:
    registry = CoreRegistry()
    bus = CoreMessageBus()

    cores = [
        TerraCore(), AquaCore(), AeroCore(), VitaCore(),
        SophiaCore(), GuardianCore(), NexusCore(), EtaCore(),
    ]
    for core in cores:
        registry.register(core)
        bus.register(core)

    # Allow TERRA -> SOPHIA on gaia.state.*
    bus.allow("TERRA", "SOPHIA", "gaia.state.")
    # Allow all cores to broadcast on gaia.state.*
    for core in cores:
        bus.allow(core.name, "*", "gaia.state.")

    await registry.boot()

    # Send a test message
    msg = CoreMessage(
        sender="TERRA",
        recipient="SOPHIA",
        topic="gaia.state.update/v1",
        payload={"temperature_c": 14.2, "humidity_pct": 62.0},
        trust_label="bounded",
    )
    await bus.dispatch(msg)

    # Print health table
    print("\n=== Health Table ===")
    for name, status in registry.health_table().items():
        print(f"  {name:<12} {status.value}")

    # Print snapshots
    print("\n=== State Snapshots ===")
    for snap in registry.snapshot_all():
        print(f"  {snap.core_name:<12} health={snap.health.value} state={snap.state}")

    await registry.shutdown()
    print("\n[gaia] shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
