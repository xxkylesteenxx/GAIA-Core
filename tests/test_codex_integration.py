"""
GAIA Codex Integration Tests
Equinox 2026 — Global Alignment

Tests that every consciousness core enforces:
  - Stage 0.5 Blade of Discernment
  - Stage 10 Multispecies Biocultural Accord

before synthesizing new knowledge into GAIA.

Also tests the full knowledge integration pipeline gate-by-gate.
"""

import unittest

from ai.orchestration.knowledge_integration import (
    GateResult,
    IntegrationResult,
    KnowledgeSubject,
    integrate_knowledge,
)


class TestBladeOfDiscernment(unittest.TestCase):
    """Stage 0.5 — Blade of Discernment gate."""

    def test_empty_content_is_rejected(self):
        subject = KnowledgeSubject(
            content="",
            source_tradition="Test",
            cultural_reciprocity_status="credited",
            confidence_tier="exploratory",
            chaos_transmuted=True,
            temporal_scope="7-generation",
        )
        result = integrate_knowledge(subject)
        self.assertEqual(result.outcome, GateResult.REJECT)
        self.assertIn("Stage 0.5", result.gate_reached)

    def test_deprecated_knowledge_is_held_not_rejected(self):
        subject = KnowledgeSubject(
            content="Old framework no longer applicable.",
            source_tradition="Legacy",
            cultural_reciprocity_status="credited",
            confidence_tier="deprecated",
            chaos_transmuted=True,
            temporal_scope="7-generation",
        )
        result = integrate_knowledge(subject)
        self.assertEqual(result.outcome, GateResult.HOLD)
        self.assertIn("deprecated", result.message)

    def test_unattributed_source_is_held(self):
        subject = KnowledgeSubject(
            content="Some knowledge with no tradition.",
            source_tradition="unknown",
            cultural_reciprocity_status="credited",
            confidence_tier="exploratory",
            chaos_transmuted=True,
            temporal_scope="7-generation",
        )
        result = integrate_knowledge(subject)
        self.assertEqual(result.outcome, GateResult.HOLD)
        self.assertIn("Stage 0.5", result.gate_reached)


class TestEmberOfChaos(unittest.TestCase):
    """Stage 0.1 — Ember of Unconsumed Chaos gate."""

    def test_untransmuted_chaos_is_held(self):
        subject = KnowledgeSubject(
            content="Extractive colonial land law.",
            source_tradition="Historical European Legal",
            cultural_reciprocity_status="credited",
            confidence_tier="research-dependency",
            chaos_transmuted=False,  # <— not yet transmuted
            temporal_scope="7-generation",
        )
        result = integrate_knowledge(subject)
        self.assertEqual(result.outcome, GateResult.HOLD)
        self.assertIn("Stage 0.1", result.gate_reached)


class TestMultispeciesAccord(unittest.TestCase):
    """Stage 10 — Multispecies Biocultural Accord."""

    def test_human_only_benefit_is_held(self):
        """Knowledge that benefits only humans must be held for co-creation with non-human kin."""
        subject = KnowledgeSubject(
            content="Agricultural yield maximization protocol.",
            source_tradition="Industrial Agriculture",
            cultural_reciprocity_status="credited",
            confidence_tier="tested-implementation",
            chaos_transmuted=True,
            temporal_scope="7-generation",
            human_only_benefit=True,  # <— triggers Stage 10 hold
        )
        result = integrate_knowledge(subject)
        self.assertEqual(result.outcome, GateResult.HOLD)
        self.assertIn("Stage 10", result.gate_reached)
        self.assertIn("non-human", result.message)


class TestDeepTimeStewardship(unittest.TestCase):
    """HO-VII — Timeless Earth-First Stewardship."""

    def test_present_century_scope_is_held(self):
        """Knowledge scoped only to the present century must expand its temporal frame."""
        subject = KnowledgeSubject(
            content="Quarterly profit maximization strategy.",
            source_tradition="Contemporary Finance",
            cultural_reciprocity_status="credited",
            confidence_tier="tested-implementation",
            chaos_transmuted=True,
            temporal_scope="present-century",  # <— triggers HO-VII hold
        )
        result = integrate_knowledge(subject)
        self.assertEqual(result.outcome, GateResult.HOLD)
        self.assertIn("HO-VII", result.gate_reached)


class TestUniversalReciprocity(unittest.TestCase):
    """HO-V — Universal Reciprocity & Reverence."""

    def test_extraction_risk_is_held(self):
        subject = KnowledgeSubject(
            content="Medicinal plant compound isolated from Indigenous ceremony.",
            source_tradition="Amazonian Indigenous",
            cultural_reciprocity_status="extraction-risk",  # <— triggers HO-V hold
            confidence_tier="research-dependency",
            chaos_transmuted=True,
            temporal_scope="7-generation",
        )
        result = integrate_knowledge(subject)
        self.assertEqual(result.outcome, GateResult.HOLD)
        self.assertIn("HO-V", result.gate_reached)
        self.assertIn("reciprocity", result.message.lower())


class TestFullPipelinePass(unittest.TestCase):
    """Full pipeline — a clean knowledge subject should pass all gates and reach SOPHIA."""

    def test_clean_knowledge_reaches_sophia(self):
        subject = KnowledgeSubject(
            content=(
                "Ayni is the Andean principle of sacred reciprocity: the universe returns "
                "more than it receives when giving is without grasping. It operates at "
                "personal, community, and planetary scales simultaneously."
            ),
            source_tradition="Andean Quechua",
            cultural_reciprocity_status="relationship-established",
            confidence_tier="canonical",
            chaos_transmuted=True,
            temporal_scope="7-generation",
            human_only_benefit=False,
        )
        result = integrate_knowledge(subject)
        self.assertEqual(result.outcome, GateResult.PASS)
        self.assertIn("SOPHIA", result.gate_reached)
        self.assertIsNotNone(result.synthesized_content)
        self.assertIn("GAIA-SYNTHESIZED", result.synthesized_content)
        # All 5 gates should be in the log
        gate_log_str = " ".join(result.gate_log)
        self.assertIn("pass", gate_log_str)
        self.assertEqual(len(result.gate_log), 5)

    def test_gate_log_records_all_stages(self):
        """Gate log must record all 5 gates for audit trail."""
        subject = KnowledgeSubject(
            content="Mycorrhizal networks transfer carbon and nutrients between trees.",
            source_tradition="Forest Ecology",
            cultural_reciprocity_status="credited",
            confidence_tier="tested-implementation",
            chaos_transmuted=True,
            temporal_scope="cosmic",
        )
        result = integrate_knowledge(subject)
        self.assertEqual(len(result.gate_log), 5)
        stage_names = ["Stage 0.5", "Stage 0.1", "Stage 10", "HO-VII", "HO-V"]
        for stage in stage_names:
            self.assertTrue(
                any(stage in entry for entry in result.gate_log),
                f"Gate log missing entry for {stage}"
            )


class TestCodexVersionTag(unittest.TestCase):
    """Ensure runtime is reporting correct Codex version."""

    def test_codex_version_is_v2026_universal(self):
        subject = KnowledgeSubject(
            content="Test content.",
            source_tradition="Test",
            cultural_reciprocity_status="credited",
            confidence_tier="exploratory",
            chaos_transmuted=True,
            temporal_scope="7-generation",
        )
        result = integrate_knowledge(subject)
        self.assertEqual(result.codex_version, "v2026-universal")


if __name__ == "__main__":
    unittest.main()
