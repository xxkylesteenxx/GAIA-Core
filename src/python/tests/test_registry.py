"""Integration tests for CoreRegistry, GaiaMessageBus, and StatePropagator.

Uses SimpleGaiaCore throughout to avoid domain-specific boilerplate.
"""

from __future__ import annotations

import asyncio
import unittest

from gaia_cores.models import GaiaMessage, HealthStatus, StateUpdate
from gaia_cores.propagation import StatePropagator
from gaia_cores.registry import CoreRegistry
from gaia_cores.simple_core import SimpleGaiaCore


def make_core(core_id: str, domain: str = "test") -> SimpleGaiaCore:
    return SimpleGaiaCore(core_id=core_id, domain=domain, summary=f"{core_id} test core")


class TestRegistryLifecycle(unittest.IsolatedAsyncioTestCase):

    async def test_register_and_boot(self) -> None:
        registry = CoreRegistry()
        await registry.register_many([make_core("ALPHA"), make_core("BETA")])
        await registry.boot_all()

        health = await registry.health_table()
        self.assertEqual(health["ALPHA"].status, HealthStatus.HEALTHY)
        self.assertEqual(health["BETA"].status, HealthStatus.HEALTHY)

        await registry.stop_all()
        health = await registry.health_table()
        self.assertEqual(health["ALPHA"].status, HealthStatus.STOPPED)

    async def test_duplicate_registration_raises(self) -> None:
        registry = CoreRegistry()
        await registry.register(make_core("DUP"))
        with self.assertRaises(ValueError):
            await registry.register(make_core("DUP"))

    async def test_core_ids_returns_registered(self) -> None:
        registry = CoreRegistry()
        await registry.register_many([make_core("X"), make_core("Y"), make_core("Z")])
        self.assertIn("X", registry.core_ids)
        self.assertIn("Z", registry.core_ids)


class TestRegistryMessaging(unittest.IsolatedAsyncioTestCase):

    async def test_send_delivers_to_recipient(self) -> None:
        registry = CoreRegistry()
        guardian = make_core("GUARDIAN", "safety and ethics")
        nexus = make_core("NEXUS", "coordination")
        await registry.register_many([guardian, nexus])
        await registry.boot_all()

        await registry.send(
            GaiaMessage(
                sender="NEXUS",
                recipient="GUARDIAN",
                topic="policy_check",
                payload={"action": "propagate_state"},
            )
        )

        snap = registry.snapshot_all()
        self.assertIn("msg::policy_check", snap["GUARDIAN"].values)
        self.assertNotIn("msg::policy_check", snap["NEXUS"].values)
        await registry.stop_all()

    async def test_broadcast_message_reaches_all(self) -> None:
        registry = CoreRegistry()
        await registry.register_many([make_core("A"), make_core("B"), make_core("C")])
        await registry.boot_all()

        await registry.send(
            GaiaMessage(
                sender="SYSTEM",
                recipient=None,
                topic="system_alert",
                payload={"level": "info"},
            )
        )

        snaps = registry.snapshot_all()
        for core_id in ("A", "B", "C"):
            self.assertIn("msg::system_alert", snaps[core_id].values)
        await registry.stop_all()


class TestStatePropagator(unittest.IsolatedAsyncioTestCase):

    async def test_selective_delivers_to_targets_only(self) -> None:
        registry = CoreRegistry()
        terra   = make_core("TERRA", "earth-system sensing")
        guardian = make_core("GUARDIAN", "safety and ethics")
        nexus   = make_core("NEXUS", "coordination")
        await registry.register_many([terra, guardian, nexus])
        await registry.boot_all()

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

        snaps = registry.snapshot_all()
        self.assertIn("state::hydrology", snaps["TERRA"].values)
        self.assertIn("state::hydrology", snaps["GUARDIAN"].values)
        self.assertNotIn("state::hydrology", snaps["NEXUS"].values)
        await registry.stop_all()

    async def test_broadcast_reaches_all_cores(self) -> None:
        registry = CoreRegistry()
        await registry.register_many([
            make_core("TERRA"), make_core("AQUA"), make_core("AERO"),
        ])
        await registry.boot_all()

        propagator = StatePropagator(registry)
        await propagator.broadcast(
            StateUpdate(
                source="planetary_ingest",
                scope="global",
                values={"temperature_anomaly_c": 1.29},
                summary="Planetary baseline loaded",
            )
        )

        snaps = registry.snapshot_all()
        for core_id in ("TERRA", "AQUA", "AERO"):
            self.assertIn("state::global", snaps[core_id].values)
        await registry.stop_all()

    async def test_health_table_after_boot(self) -> None:
        registry = CoreRegistry()
        await registry.register_many([
            make_core("GUARDIAN"), make_core("NEXUS"), make_core("TERRA"),
        ])
        await registry.boot_all()

        health = await registry.health_table()
        self.assertEqual(health["GUARDIAN"].status.value, "healthy")
        self.assertEqual(health["NEXUS"].status.value,    "healthy")
        self.assertEqual(health["TERRA"].status.value,    "healthy")
        await registry.stop_all()


class TestSnapshotState(unittest.IsolatedAsyncioTestCase):

    async def test_snapshot_contains_message_and_state_keys(self) -> None:
        registry = CoreRegistry()
        await registry.register_many([
            make_core("GUARDIAN"), make_core("NEXUS"), make_core("TERRA"),
        ])
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

        snaps = registry.snapshot_all()
        self.assertIn("msg::policy_check",  snaps["GUARDIAN"].values)
        self.assertIn("state::hydrology",   snaps["GUARDIAN"].values)
        self.assertIn("state::hydrology",   snaps["TERRA"].values)
        await registry.stop_all()


if __name__ == "__main__":
    unittest.main()
