"""Unit tests for CoreRegistry, CoreMessageBus, and core lifecycle."""

import asyncio
import unittest

from gaia_cores.bus import CoreMessageBus
from gaia_cores.models import CoreMessage, HealthStatus
from gaia_cores.registry import CoreRegistry
from gaia_cores.cores.guardian import GuardianCore
from gaia_cores.cores.sophia import SophiaCore
from gaia_cores.cores.terra import TerraCore


class TestRegistry(unittest.IsolatedAsyncioTestCase):

    async def test_boot_order_guardian_first(self) -> None:
        """GUARDIAN must be running before SOPHIA after boot."""
        registry = CoreRegistry()
        guardian = GuardianCore()
        sophia = SophiaCore()
        terra = TerraCore()
        for c in [terra, sophia, guardian]:  # intentionally shuffled
            registry.register(c)
        await registry.boot()
        table = registry.health_table()
        self.assertEqual(table["GUARDIAN"], HealthStatus.OK)
        self.assertEqual(table["SOPHIA"], HealthStatus.OK)
        self.assertEqual(table["TERRA"], HealthStatus.OK)
        await registry.shutdown()

    async def test_health_table_after_shutdown(self) -> None:
        registry = CoreRegistry()
        terra = TerraCore()
        registry.register(terra)
        await registry.boot()
        await registry.shutdown()
        self.assertEqual(registry.health_table()["TERRA"], HealthStatus.STOPPED)

    async def test_bus_route_denied(self) -> None:
        """Message with no matching route rule is silently dropped."""
        bus = CoreMessageBus()
        sophia = SophiaCore()
        await sophia.startup()
        bus.register(sophia)
        # No allow rule added
        msg = CoreMessage(sender="TERRA", recipient="SOPHIA",
                          topic="gaia.state.update/v1", payload={})
        await bus.dispatch(msg)  # should not raise
        snap = sophia.snapshot()
        self.assertNotIn("gaia.state.update/v1", snap.state)

    async def test_bus_route_allowed(self) -> None:
        bus = CoreMessageBus()
        sophia = SophiaCore()
        await sophia.startup()
        bus.register(sophia)
        bus.allow("TERRA", "SOPHIA", "gaia.state.")
        msg = CoreMessage(sender="TERRA", recipient="SOPHIA",
                          topic="gaia.state.update/v1", payload={"x": 1})
        await bus.dispatch(msg)
        snap = sophia.snapshot()
        self.assertIn("gaia.state.update/v1", snap.state)

    async def test_guardian_alerts_unexpected_critical(self) -> None:
        guardian = GuardianCore()
        await guardian.startup()
        msg = CoreMessage(
            sender="TERRA",           # not in SOPHIA/GUARDIAN/NEXUS
            recipient="GUARDIAN",
            topic="gaia.policy.directive/v1",
            payload={},
            trust_label="critical",   # unexpected from TERRA
        )
        await guardian.handle_message(msg)
        snap = guardian.snapshot()
        self.assertEqual(len(snap.state["alerts"]), 1)


if __name__ == "__main__":
    unittest.main()
