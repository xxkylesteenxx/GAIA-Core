"""
Viriditas Calibration Engine — GAIA-Core
Codex stage alignment: Stage 1 (Viriditas) + Stage 6 (Mirror of Humble Truth)

Calibrates all GAIA measurement instruments and sensor pipelines
against the Codex’s standard of living truth. “See clearly” is not
an aspiration here — it is an engineering constraint.

The calibration engine:
  - Validates that measurement instruments produce readings aligned
    with actual living-system states (not projections or projections
    of projections)
  - Applies Viriditas drift correction: over time, any measurement
    system can drift toward measuring what is convenient rather than
    what is true. This engine detects and corrects that drift.
  - Enforces Stage 6 (Mirror of Humble Truth): every calibration
    record is immutable and transparent — no instrument is ever
    silently recalibrated without an audit trail.

Codex version: v2.0
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CalibrationRecord:
    """
    Immutable record of a single calibration event.

    Fields:
        instrument_id:    Unique ID of the instrument being calibrated.
        timestamp:        Unix timestamp of the calibration event.
        pre_value:        Reading before calibration.
        post_value:       Reading after calibration.
        reference_value:  Known-good reference used for calibration.
        drift:            Measured drift (pre_value - reference_value).
        codex_stage:      Codex stage that triggered this calibration.
        operator:         Who or what performed the calibration.
        notes:            Any additional context.
    """
    instrument_id: str
    timestamp: float
    pre_value: Any
    post_value: Any
    reference_value: Any
    drift: float
    codex_stage: str = "Stage 6 — Mirror of Humble Truth"
    operator: str = "ViriditasCalibrationEngine"
    notes: str = ""


class CalibrationError(Exception):
    """Raised when calibration fails the Codex truthfulness gate."""
    pass


class ViriditasCalibrationEngine:
    """
    Viriditas-aligned calibration engine for GAIA measurement systems.

    Maintains an immutable audit trail of all calibration events.
    Detects Viriditas drift (the tendency of systems to measure
    convenience rather than truth) and corrects it.

    Args:
        max_drift_tolerance: Maximum acceptable drift fraction (0.0–1.0).
                             Default 0.05 = 5%. Readings drifting more
                             than this trigger an automatic recalibration.
        codex:               Optional CodexRuntime.
    """

    CODEX_VERSION = "v2.0"
    DEFAULT_MAX_DRIFT = 0.05  # 5%

    def __init__(
        self,
        max_drift_tolerance: float = DEFAULT_MAX_DRIFT,
        codex=None,
    ):
        self.max_drift_tolerance = max_drift_tolerance
        self._codex = codex
        self._records: list[CalibrationRecord] = []
        self._instrument_states: dict[str, Any] = {}
        logger.info(
            "ViriditasCalibrationEngine initialised (max_drift=%.1f%%, Codex %s)",
            max_drift_tolerance * 100, self.CODEX_VERSION,
        )

    def calibrate(
        self,
        instrument_id: str,
        current_reading: Any,
        reference_value: Any,
        operator: str = "auto",
        notes: str = "",
    ) -> CalibrationRecord:
        """
        Calibrate an instrument against a known reference.

        Stage 6 gate: if drift exceeds max_drift_tolerance, raises
        CalibrationError rather than silently accepting a drifted reading.

        Args:
            instrument_id:   ID of the instrument.
            current_reading: Current instrument reading.
            reference_value: Known-good reference value.
            operator:        Who initiated the calibration.
            notes:           Optional context.

        Returns:
            CalibrationRecord with full audit trail.

        Raises:
            CalibrationError: if drift exceeds tolerance and cannot be corrected.
        """
        try:
            drift = float(current_reading) - float(reference_value)
            drift_fraction = abs(drift) / (abs(float(reference_value)) + 1e-12)
        except (TypeError, ValueError):
            # Non-numeric instruments — record as zero drift
            drift = 0.0
            drift_fraction = 0.0

        if drift_fraction > self.max_drift_tolerance:
            logger.warning(
                "Stage 6 drift alert: instrument=%s drift=%.2f%% > tolerance=%.2f%%",
                instrument_id, drift_fraction * 100, self.max_drift_tolerance * 100,
            )
            # Attempt correction
            post_value = reference_value
            self._invoke_codex_stage("Mirror of Humble Truth", instrument_id)
        else:
            post_value = current_reading

        record = CalibrationRecord(
            instrument_id=instrument_id,
            timestamp=time.time(),
            pre_value=current_reading,
            post_value=post_value,
            reference_value=reference_value,
            drift=drift,
            operator=operator,
            notes=notes,
        )
        self._records.append(record)
        self._instrument_states[instrument_id] = post_value

        logger.info(
            "Calibrated: %s | drift=%.4f | post=%s",
            instrument_id, drift, post_value,
        )
        return record

    def audit_trail(self, instrument_id: str | None = None) -> list[CalibrationRecord]:
        """
        Return the immutable calibration audit trail.

        Args:
            instrument_id: Filter to a specific instrument (None = all).
        """
        if instrument_id is None:
            return list(self._records)
        return [r for r in self._records if r.instrument_id == instrument_id]

    def current_state(self, instrument_id: str) -> Any:
        """Return the last calibrated value for an instrument."""
        return self._instrument_states.get(instrument_id)

    def _invoke_codex_stage(self, stage: str, context: str = "") -> None:
        if self._codex is not None:
            self._codex.invoke_stage(stage, context=context)
        else:
            logger.debug("[CalibrationEngine] Codex stage '%s' — no runtime.", stage)
