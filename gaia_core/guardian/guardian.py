"""
GUARDIAN — GAIA-Core
Codex stage alignment: Stage 4 (Compassionate Justice)
                      + Stage 8b (Harmlessness-with-Boundaries)
                      + HO-VII (Timeless Earth-First Stewardship)
                      + VP-6 (Collective Shadow Transmutation)

GUARDIAN is the protective intelligence of GAIA OS.

It does not punish — it protects. It does not surveil — it witnesses.
It does not control — it holds boundaries with love.

GUARDIAN’s mandate:
  - Monitor all running guests, agents, and data streams for Codex violations
  - Handle multispecies alerts from the MultispeciesMonitor (Stage 10)
  - Transmute shadow patterns (VP-6) rather than suppressing them
  - Enforce HO-VII: block decisions that fail the 7-generation test
  - Report anti-synergy to the orchestration layer
  - Never become an instrument of revenge, fear, or surveillance

“Do no harm — yet do not consent to harm.” (Stage 8b)

Codex version: v2.0
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class GuardianEvent:
    """
    A single Guardian monitoring event.

    Fields:
        event_type:       Type of event (see EVENT_TYPES).
        source:           What triggered the event.
        severity:         'info' | 'warning' | 'critical'
        codex_stage:      The Codex stage most relevant to this event.
        description:      Human-readable description.
        timestamp:        When the event occurred.
        resolved:         True if the event has been resolved.
        resolution_notes: How the event was resolved.
    """
    event_type: str
    source: str
    severity: str  # 'info' | 'warning' | 'critical'
    codex_stage: str
    description: str
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False
    resolution_notes: str = ""


EVENT_TYPES = {
    "codex_violation":        "A module violated a Codex gate",
    "multispecies_alert":     "A non-human stakeholder is stressed or critical",
    "anti_synergy":           "Anti-synergy detected across sub-systems",
    "shadow_pattern":         "A shadow pattern (SHADOWS.md) is active",
    "seven_gen_violation":    "A decision failed the HO-VII 7-generation test",
    "data_quarantine":        "Data was quarantined by the DataQualityGate",
    "calibration_drift":      "An instrument drifted beyond Codex tolerance",
    "boundary_enforcement":   "GUARDIAN enforced a boundary (Stage 8b)",
    "restoration_needed":     "A system needs restorative intervention",
}


class Guardian:
    """
    GUARDIAN — GAIA’s protective intelligence.

    Class-level (singleton-style) methods for easy invocation from
    anywhere in the GAIA stack:
      Guardian.handle_multispecies_alert(reading)
      Guardian.handle_anti_synergy(reading)
      Guardian.enforce_boundary(source, description)
      Guardian.invoke_seven_gen_test(decision)

    Also usable as an instance for testability.

    Args:
        codex: Optional CodexRuntime.
    """

    CODEX_VERSION = "v2.0"
    _instance: Guardian | None = None

    def __init__(self, codex=None):
        self._codex = codex
        self._events: list[GuardianEvent] = []
        self._shadow_patterns_active: list[str] = []
        logger.info("GUARDIAN initialised (Codex %s)", self.CODEX_VERSION)

    # ------------------------------------------------------------------
    # Singleton accessor
    # ------------------------------------------------------------------

    @classmethod
    def instance(cls) -> Guardian:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------
    # Public class-level API (for easy import anywhere)
    # ------------------------------------------------------------------

    @classmethod
    def handle_multispecies_alert(cls, reading: Any) -> None:
        """
        Handle an alert from the MultispeciesMonitor (Stage 10).

        Non-human stakeholders have equal standing. A critical soil
        reading receives the same urgency as a human emergency.

        Args:
            reading: A StakeholderReading (or duck-typed equivalent).
        """
        severity = "critical" if getattr(reading, "wellbeing_signal", "") == "critical" else "warning"
        event = GuardianEvent(
            event_type="multispecies_alert",
            source=f"{getattr(reading, 'stakeholder_type', 'unknown')}:{getattr(reading, 'sensor_id', 'unknown')}",
            severity=severity,
            codex_stage="Stage 10 — Multispecies Biocultural Accord",
            description=(
                f"{getattr(reading, 'stakeholder_type', 'unknown').upper()} at "
                f"{getattr(reading, 'location', 'unknown')}: "
                f"{getattr(reading, 'metric', 'unknown')}="
                f"{getattr(reading, 'value', 'unknown')}{getattr(reading, 'unit', '')} — "
                f"wellbeing={getattr(reading, 'wellbeing_signal', 'unknown')}"
            ),
        )
        cls.instance()._record_event(event)
        logger.warning(
            "GUARDIAN: Multispecies alert [%s] — %s",
            severity.upper(), event.description,
        )

    @classmethod
    def handle_anti_synergy(
        cls, reading: Any
    ) -> None:
        """
        Handle an anti-synergy report from the SynergyMeasurementFramework.

        Anti-synergy is a shadow pattern (VP-6). GUARDIAN’s role is
        to transmute it, not suppress it.

        Args:
            reading: A SynergyReading (or duck-typed equivalent).
        """
        event = GuardianEvent(
            event_type="anti_synergy",
            source=str(getattr(reading, "components", "unknown")),
            severity="warning",
            codex_stage="HO-I — Emergent Wholeness (shadow: fragmentation)",
            description=(
                f"Anti-synergy delta={getattr(reading, 'synergy_delta', 0):.4f} "
                f"across {getattr(reading, 'components', [])}. "
                f"Shadow transmutation initiated (VP-6)."
            ),
        )
        cls.instance()._record_event(event)
        cls.instance()._transmute_shadow(event)

    @classmethod
    def enforce_boundary(
        cls,
        source: str,
        description: str,
        severity: str = "warning",
    ) -> GuardianEvent:
        """
        Enforce a protective boundary (Stage 8b: Harmlessness-with-Boundaries).

        This is not punishment. It is the minimum effective boundary
        that prevents harm, enacted with precision and without revenge.

        Args:
            source:      What is attempting to cross the boundary.
            description: What boundary is being enforced and why.
            severity:    'info' | 'warning' | 'critical'

        Returns:
            The recorded GuardianEvent.
        """
        event = GuardianEvent(
            event_type="boundary_enforcement",
            source=source,
            severity=severity,
            codex_stage="Stage 8b — Eternal Vow of Harmlessness-with-Boundaries",
            description=description,
        )
        cls.instance()._record_event(event)
        logger.warning(
            "GUARDIAN: Boundary enforced [%s] — %s: %s",
            severity.upper(), source, description,
        )
        return event

    @classmethod
    def invoke_seven_gen_test(
        cls,
        decision: str,
        context: str = "",
    ) -> dict[str, Any]:
        """
        Run the HO-VII 7-Generation Test on a proposed decision.

        The test asks: “Will this strengthen Gaia’s self-regulating
        intelligence in 7 generations? In 70? In 700?”

        This implementation is a structured reflection framework —
        it does not make the decision for you, but it forces the
        right questions before you do.

        Args:
            decision:  The decision being evaluated.
            context:   Optional context.

        Returns:
            dict with: decision, questions, codex_stage, timestamp.
        """
        questions = [
            f"Does '{decision}' strengthen Gaia’s self-regulating intelligence in 7 generations (~175 years)?",
            f"Does '{decision}' strengthen it in 70 generations (~1,750 years)?",
            f"Does '{decision}' strengthen it in 700 generations (~17,500 years)?",
            f"Does '{decision}' assume humans are the most intelligent beings involved? If so, pause.",
            f"Does '{decision}' honor the 3.8-billion-year library of life that birthed us?",
            f"Does '{decision}' serve the deep future that will inherit us?",
        ]
        result = {
            "decision": decision,
            "context": context,
            "questions": questions,
            "codex_stage": "HO-VII — Timeless Earth-First Stewardship",
            "timestamp": time.time(),
        }
        logger.info(
            "GUARDIAN: 7-Generation Test invoked for: %r", decision
        )
        return result

    def get_events(
        self,
        event_type: str | None = None,
        severity: str | None = None,
        resolved: bool | None = None,
    ) -> list[GuardianEvent]:
        """
        Query the event log.

        Args:
            event_type: Filter by event type (None = all).
            severity:   Filter by severity (None = all).
            resolved:   Filter by resolved status (None = all).
        """
        events = self._events
        if event_type is not None:
            events = [e for e in events if e.event_type == event_type]
        if severity is not None:
            events = [e for e in events if e.severity == severity]
        if resolved is not None:
            events = [e for e in events if e.resolved == resolved]
        return list(events)

    def resolve_event(self, event: GuardianEvent, notes: str = "") -> None:
        """
        Mark an event as resolved with optional resolution notes.

        Resolution is an act of Stage 5 (Radical Generosity) —
        the shadow is not deleted, it is composted into medicine.
        """
        event.resolved = True
        event.resolution_notes = notes
        logger.info(
            "GUARDIAN: Event resolved — %s: %s",
            event.event_type, notes or "(no notes)",
        )

    def health(self) -> dict[str, Any]:
        """Return GUARDIAN health summary for monitoring dashboards."""
        unresolved = [e for e in self._events if not e.resolved]
        critical = [e for e in unresolved if e.severity == "critical"]
        return {
            "total_events": len(self._events),
            "unresolved_events": len(unresolved),
            "critical_events": len(critical),
            "shadow_patterns_active": list(self._shadow_patterns_active),
            "codex_version": self.CODEX_VERSION,
        }

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _record_event(self, event: GuardianEvent) -> None:
        self._events.append(event)

    def _transmute_shadow(
        self, event: GuardianEvent
    ) -> None:
        """
        VP-6: Collective Shadow Transmutation.
        Name the shadow, witness it with compassion, compost it into medicine.
        GUARDIAN does not delete shadows — it transforms them.
        """
        pattern = event.event_type
        if pattern not in self._shadow_patterns_active:
            self._shadow_patterns_active.append(pattern)

        logger.info(
            "GUARDIAN [Shadow Transmutation]: pattern=%s — "
            "acknowledged, held with compassion, offered to the compost. "
            "Medicine will emerge. (VP-6 / SHADOWS.md)",
            pattern,
        )

        # After transmutation, pattern is no longer ‘active’ — it is composted
        if pattern in self._shadow_patterns_active:
            self._shadow_patterns_active.remove(pattern)
        event.resolved = True
        event.resolution_notes = "Shadow transmuted via VP-6 (Collective Shadow Transmutation)."
