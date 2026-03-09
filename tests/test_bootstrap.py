from pathlib import Path
import shutil
import tempfile
import unittest

from gaia_core.bootstrap import build_default_gaia
from gaia_core.grounding.environment import classify_freshness


class GaiaBootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix="gaia-test-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_builds_all_eight_cores(self) -> None:
        gaia = build_default_gaia(self.tmpdir)
        self.assertEqual(len(gaia.registry.names()), 8)
        self.assertIn("NEXUS", gaia.registry.names())
        self.assertIn("VITA", gaia.registry.names())

    def test_checkpoint_and_replay_exist(self) -> None:
        gaia = build_default_gaia(self.tmpdir)
        gaia.dispatch("SOPHIA", {"kind": "summarize", "payload": {"text": "hello"}})
        snapshot = gaia.consciousness_snapshot()
        self.assertGreaterEqual(snapshot["memory_event_count"], 1)
        ckpt = gaia.checkpoint()
        self.assertTrue(ckpt["checkpoint_id"].startswith("ckpt_"))

    def test_freshness_classes(self) -> None:
        self.assertEqual(classify_freshness(10), "URT")
        self.assertEqual(classify_freshness(1800), "RT")
        self.assertEqual(classify_freshness(4000), "NRT")


if __name__ == "__main__":
    unittest.main()
