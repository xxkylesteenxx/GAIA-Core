"""
Synergy Measurement Framework — GAIA-Core
Codex stage alignment: Stage 2 (Magnum Opus) + HO-II (Eternal Recursion)
                      + VP-2 (Cross-Scale Pattern Recognition)

Measures synergy: the degree to which the combined effect of a system’s
parts exceeds (or falls below) the sum of their individual effects.

In Codex terms: synergy is the measurable signature of Emergent Wholeness
(HO-I). When a system is functioning in Codex alignment, synergy is
positive and compounding. When a system is in shadow, synergy is negative
or absent — parts work against each other.

The framework:
  - Measures synergy across any set of GAIA sub-systems or consciousness cores
  - Detects anti-synergy (shadow patterns) and reports them to GUARDIAN
  - Tracks synergy over time to detect Viriditas drift
  - Supports multi-scale measurement (personal → team → planetary)

Codex version: v2.0
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SynergyReading:
    """
    A single synergy measurement across a set of components.

    Fields:
        components:         Names of the components being measured.
        individual_scores:  Score for each component in isolation.
        combined_score:     Score of the system as a whole.
        synergy_delta:      combined_score - sum(individual_scores).
        synergy_ratio:      combined_score / sum(individual_scores).
        timestamp:          When the measurement was taken.
        scale:              'personal' | 'team' | 'planetary'
        codex_aligned:      True if synergy_delta > 0 (emergent wholeness).
        notes:              Optional context.
    """
    components: list[str]
    individual_scores: dict[str, float]
    combined_score: float
    synergy_delta: float
    synergy_ratio: float
    timestamp: float = field(default_factory=time.time)
    scale: str = "team"
    codex_aligned: bool = True
    notes: str = ""


class SynergyMeasurementFramework:
    """
    Measures emergent synergy across GAIA sub-systems.

    A synergy_delta > 0 indicates Codex alignment (HO-I: Emergent Wholeness).
    A synergy_delta < 0 indicates shadow patterns and is reported to GUARDIAN.

    Args:
        scale:  Default measurement scale ('personal'|'team'|'planetary').
        codex:  Optional CodexRuntime.
    """

    CODEX_VERSION = "v2.0"

    def __init__(self, scale: str = "team", codex=None):
        self.scale = scale
        self._codex = codex
        self._history: list[SynergyReading] = []
        logger.info(
            "SynergyMeasurementFramework initialised (scale=%s, Codex %s)",
            scale, self.CODEX_VERSION,
        )

    def measure(
        self,
        components: list[str],
        individual_scores: dict[str, float],
        combined_score: float,
        scale: str | None = None,
        notes: str = "",
    ) -> SynergyReading:
        """
        Measure synergy across a set of components.

        Args:
            components:        Names of the components.
            individual_scores: Score for each component in isolation.
                               Keys must match components list.
            combined_score:    Measured score of the combined system.
            scale:             Override default scale.
            notes:             Optional context.

        Returns:
            SynergyReading with full synergy analysis.
        """
        total_individual = sum(individual_scores.get(c, 0.0) for c in components)
        synergy_delta = combined_score - total_individual
        synergy_ratio = (
            combined_score / total_individual
            if abs(total_individual) > 1e-12
            else 1.0
        )
        codex_aligned = synergy_delta >= 0

        reading = SynergyReading(
            components=list(components),
            individual_scores=dict(individual_scores),
            combined_score=combined_score,
            synergy_delta=synergy_delta,
            synergy_ratio=synergy_ratio,
            scale=scale or self.scale,
            codex_aligned=codex_aligned,
            notes=notes,
        )
        self._history.append(reading)

        if not codex_aligned:
            logger.warning(
                "Anti-synergy detected: delta=%.4f across %s — reporting to GUARDIAN.",
                synergy_delta, components,
            )
            self._report_anti_synergy(reading)
        else:
            logger.info(
                "Synergy measured: delta=+%.4f (ratio=%.3f) across %s — Codex aligned.",
                synergy_delta, synergy_ratio, components,
            )

        return reading

    def trend(self, last_n: int = 10) -> dict[str, Any]:
        """
        Return synergy trend over the last N readings.

        Useful for detecting Viriditas drift over time:
        a declining trend signals shadow accumulation.
        """
        recent = self._history[-last_n:]
        if not recent:
            return {"trend": "no_data", "readings": 0}

        deltas = [r.synergy_delta for r in recent]
        avg_delta = sum(deltas) / len(deltas)
        aligned_count = sum(1 for r in recent if r.codex_aligned)

        return {
            "average_synergy_delta": avg_delta,
            "aligned_readings": aligned_count,
            "total_readings": len(recent),
            "alignment_rate": aligned_count / len(recent),
            "trend": "rising" if deltas[-1] > deltas[0] else "falling",
            "codex_version": self.CODEX_VERSION,
        }

    def _report_anti_synergy(self, reading: SynergyReading) -> None:
        """Report anti-synergy to GUARDIAN for shadow transmutation."""
        try:
            from gaia_core.guardian.guardian import Guardian  # noqa: PLC0415
            Guardian.handle_anti_synergy(reading)
        except ImportError:
            logger.debug("GUARDIAN not available — anti-synergy logged only.")
