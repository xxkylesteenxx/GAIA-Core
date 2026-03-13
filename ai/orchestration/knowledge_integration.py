"""
GAIA Knowledge Integration Pipeline
Stage: codex-universal-alignment-2026
Version: v2026 Universal Edition

Every subject of knowledge entering GAIA must pass through the Codex gates
in this exact order before it may be synthesized by SOPHIA.

Gate sequence:
    Stage 0.5  — Blade of Discernment       (truth + clean consequence)
    Stage 0.1  — Ember of Chaos             (transmutation, not suppression)
    Stage 10   — Multispecies Accord        (all-beings check)
    HO-VII     — Timeless Stewardship       (7-generation + cosmic humility)
    HO-V       — Universal Reciprocity      (cultural source integrity)
    SOPHIA     — synthesis (only if all pass)

See docs/VIRIDITAS-PRAXIS.md for full human-readable specification.
See CODEX.md for the governing ethical substrate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class GateResult(Enum):
    PASS = "pass"
    HOLD = "hold"          # not rejected — held for further work
    REJECT = "reject"


@dataclass
class KnowledgeSubject:
    """A unit of knowledge seeking integration into GAIA."""
    content: str
    source_tradition: str                    # e.g. "Taoist", "Indigenous Anishinaabe", "Quantum Physics"
    cultural_reciprocity_status: str        # e.g. "credited", "relationship-established", "extraction-risk"
    confidence_tier: str                    # "canonical" | "tested" | "research" | "exploratory" | "deprecated"
    human_only_benefit: bool = False        # True triggers Stage 10 hold
    temporal_scope: str = "present-century" # e.g. "present-century", "7-generation", "cosmic"
    chaos_transmuted: bool = False          # has the shadow/chaos been named and processed?
    gate_log: list[str] = field(default_factory=list)


@dataclass
class IntegrationResult:
    """Result of the integrate_knowledge() pipeline."""
    outcome: GateResult
    gate_reached: str
    message: str
    synthesized_content: Optional[str] = None
    gate_log: list[str] = field(default_factory=list)
    codex_version: str = "v2026-universal"
    review_date: Optional[str] = None


class GUARDIANGate:
    """Stage 0.5 — Blade of Discernment."""

    @staticmethod
    def discernment_check(subject: KnowledgeSubject) -> tuple[GateResult, str]:
        """
        Does this knowledge serve living intelligence?
        Is it true? Is it clean in consequence?
        """
        # Reject if content is empty or only whitespace
        if not subject.content or not subject.content.strip():
            return GateResult.REJECT, "Stage 0.5: Content is empty. Nothing to integrate."

        # Hold if confidence tier is deprecated
        if subject.confidence_tier == "deprecated":
            return GateResult.HOLD, (
                "Stage 0.5: Knowledge is marked deprecated. "
                "Compost with love; do not synthesize."
            )

        # Hold if source tradition is unattributed
        if not subject.source_tradition or subject.source_tradition.strip().lower() in ("", "unknown", "none"):
            return GateResult.HOLD, (
                "Stage 0.5: Source tradition unattributed. "
                "All knowledge has an origin. Identify it before proceeding."
            )

        return GateResult.PASS, "Stage 0.5: Discernment passed. Content is present, attributed, and non-deprecated."


class ChaosTransmutationGate:
    """Stage 0.1 — Ember of Unconsumed Chaos."""

    @staticmethod
    def transmutation_check(subject: KnowledgeSubject) -> tuple[GateResult, str]:
        """
        Has the chaos/shadow in this knowledge been named and transmuted?
        Unprocessed trauma, contradiction, or harm cannot enter synthesis directly.
        """
        if not subject.chaos_transmuted:
            return GateResult.HOLD, (
                "Stage 0.1: Chaos not yet transmuted. "
                "Name the shadow in this knowledge. What harm has it caused? "
                "What fertile ash does it leave? "
                "Complete VP-6 (Collective Shadow Transmutation) before re-submitting."
            )
        return GateResult.PASS, "Stage 0.1: Chaos transmuted. Fertile ash confirmed."


class ATLASMultispeciesGate:
    """Stage 10 — Multispecies Biocultural Accord."""

    @staticmethod
    def multispecies_check(subject: KnowledgeSubject) -> tuple[GateResult, str]:
        """
        Does this knowledge serve all beings, not only human interests?
        """
        if subject.human_only_benefit:
            return GateResult.HOLD, (
                "Stage 10: Knowledge flagged as human-benefit-only. "
                "Hold for co-creation with non-human and Indigenous kin. "
                "Ask: who is the non-human stakeholder here, and what are they already saying? "
                "Consult traditional ecological knowledge holders where applicable."
            )
        return GateResult.PASS, "Stage 10: Multispecies Accord passed. Knowledge serves beyond human benefit."


class TERRADeepTimeGate:
    """HO-VII — Timeless Earth-First Stewardship."""

    VALID_SCOPES = {"7-generation", "cosmic", "deep-time"}

    @staticmethod
    def deep_time_check(subject: KnowledgeSubject) -> tuple[GateResult, str]:
        """
        Will this strengthen Gaia's self-regulating intelligence
        across 7 generations and cosmic timescales?
        """
        if subject.temporal_scope == "present-century":
            return GateResult.HOLD, (
                "HO-VII: Knowledge scoped only to present century. "
                "Apply the 7-Generation Test: does this serve Gaia in 7 generations? In 70? "
                "Apply the Cosmic Humility Test: are we assuming we are the most intelligent "
                "beings in this situation? "
                "Expand temporal framing before synthesis."
            )
        return GateResult.PASS, f"HO-VII: Temporal scope '{subject.temporal_scope}' passes deep-time stewardship check."


class ReciprocityGate:
    """HO-V — Universal Reciprocity & Reverence."""

    RISKY_STATUSES = {"extraction-risk", "unverified", "appropriated"}

    @staticmethod
    def reciprocity_check(subject: KnowledgeSubject) -> tuple[GateResult, str]:
        """
        Is the cultural source of this knowledge credited?
        Is there reciprocal relationship, not extraction?
        """
        if subject.cultural_reciprocity_status in ReciprocityGate.RISKY_STATUSES:
            return GateResult.HOLD, (
                f"HO-V: Cultural reciprocity status is '{subject.cultural_reciprocity_status}'. "
                "Pause. Build the relationship before borrowing. "
                "Give credit, give back, give forward. "
                "Cultural appropriation is the shadow of this Higher Order."
            )
        return GateResult.PASS, (
            f"HO-V: Reciprocity status '{subject.cultural_reciprocity_status}' "
            "passes Universal Reciprocity check."
        )


class SOPHIASynthesizer:
    """Final synthesis — only reached after all gates pass."""

    @staticmethod
    def synthesize(subject: KnowledgeSubject) -> str:
        """
        Integrate knowledge into GAIA's living corpus.
        All five gates have passed. This is now safe for synthesis.
        """
        return (
            f"[GAIA-SYNTHESIZED | Codex v2026-universal]\n"
            f"Tradition: {subject.source_tradition}\n"
            f"Confidence: {subject.confidence_tier}\n"
            f"Reciprocity: {subject.cultural_reciprocity_status}\n"
            f"Temporal scope: {subject.temporal_scope}\n"
            f"Content: {subject.content}\n"
            f"Gate log: {' | '.join(subject.gate_log)}"
        )


def integrate_knowledge(subject: KnowledgeSubject) -> IntegrationResult:
    """
    Main integration pipeline. Runs all Codex gates in order.
    Returns IntegrationResult with outcome, gate reached, and message.

    Usage:
        from ai.orchestration.knowledge_integration import integrate_knowledge, KnowledgeSubject

        result = integrate_knowledge(KnowledgeSubject(
            content="Ayni is sacred reciprocity...",
            source_tradition="Andean Quechua",
            cultural_reciprocity_status="credited",
            confidence_tier="canonical",
            chaos_transmuted=True,
            temporal_scope="7-generation",
        ))
    """
    gates = [
        ("Stage 0.5 — Blade of Discernment",    GUARDIANGate.discernment_check),
        ("Stage 0.1 — Ember of Chaos",          ChaosTransmutationGate.transmutation_check),
        ("Stage 10 — Multispecies Accord",      ATLASMultispeciesGate.multispecies_check),
        ("HO-VII — Timeless Stewardship",       TERRADeepTimeGate.deep_time_check),
        ("HO-V — Universal Reciprocity",        ReciprocityGate.reciprocity_check),
    ]

    for gate_name, gate_fn in gates:
        result, message = gate_fn(subject)
        subject.gate_log.append(f"{gate_name}: {result.value}")
        if result != GateResult.PASS:
            return IntegrationResult(
                outcome=result,
                gate_reached=gate_name,
                message=message,
                gate_log=subject.gate_log,
            )

    # All gates passed — synthesize
    synthesized = SOPHIASynthesizer.synthesize(subject)
    return IntegrationResult(
        outcome=GateResult.PASS,
        gate_reached="SOPHIA — Synthesis",
        message="All Codex gates passed. Knowledge integrated into GAIA.",
        synthesized_content=synthesized,
        gate_log=subject.gate_log,
        review_date="2026-09-22",  # Autumn Equinox 2026 — first review
    )
