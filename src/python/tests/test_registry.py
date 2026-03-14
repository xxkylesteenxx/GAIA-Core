"""Unit tests for CoreRegistry, CoreMessageBus, propagation, and GUARDIAN."""

from __future__ import annotations

import asyncio
import unittest

from gaia_cores.cores import GuardianCore, NexusCore, TerraCore
from gaia_cores.models import GaiaMessage, HealthStatus, StateUpdate
from gaia_cores.propagation import StatePropagator
from gaia_cores.registry import CoreRegistry


class RegistryTests(unittest.TestCase):

    def test_registry_boot_message_and_propagation(self) -> None:
        async def scenario() -> None:
            registry = CoreRegistry()
            await registry.register_many([TerraCore(), GuardianCore(), NexusCore()])
            await registry.boot_all()

            await registry.send(
                GaiaMessage(
                    sender="NEXUS",
                    recipient="GUARDIAN",
                    topic="policy_check",
                    payload={"action": "propagate_state"},
                )
            )

            propagator = StatePropagator(registry)
            await propagator.selective(
                StateUpdate(
                    source="TERRA",
                    scope="hydrology",
                    values={"soil_moisture": 0.41},
                    summary="Hydrology update",
                ),
                targets=["TERRA", "GUARDIAN"],
            )

            health = await registry.health_table()
            self.assertEqual(health["TERRA"].status.value, "healthy")
            self.assertEqual(health["GUARDIAN"].status.value, "healthy")

            snaps = registry.snapshot_all()
            self.assertIn("msg::policy_check", snaps["GUARDIAN"].values)
            self.assertIn("state::hydrology", snaps["TERRA"].values)
            await registry.stop_all()

        asyncio.run(scenario())


if __name__ == "__main__":
    unittest.main()
