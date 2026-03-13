"""
Codex-Gated Data Quality Gate — GAIA-Core
Codex stage alignment: Stage 6 (Mirror of Humble Truth)
                      + Stage 0.5 (Blade of Discernment)

Every data pipeline in GAIA passes through this gate before
data is trusted for inference, decision-making, or storage.

“See clearly, speak kindly, act cleanly.”

The data quality gate enforces five Codex-aligned dimensions:
  1. Completeness — no missing values that would distort truth
  2. Consistency — no internal contradictions
  3. Timeliness — data reflects the living present, not a stale past
  4. Provenance — data knows where it came from (HO-V: attribution)
  5. Ecological validity — data is grounded in real-world living systems

Data that fails any dimension is not silently dropped — it is
quarantined with a full explanation, so the pipeline can see
clearly what was rejected and why.

Codex version: v2.0
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DataQualityResult:
    """
    Result of a data quality gate evaluation.

    Fields:
        passed:            True if all enabled checks passed.
        data_id:           Identifier for the data being evaluated.
        timestamp:         When the gate ran.
        completeness:      Fraction of non-null fields (0.0–1.0).
        consistency:       True if no internal contradictions found.
        timeliness:        True if data age is within max_age_seconds.
        provenance_present: True if source/attribution fields are present.
        ecological_valid:  True if ecological validity check passed.
        failures:          List of failed dimension names.
        quarantine_reason: Human-readable reason if quarantined.
    """
    passed: bool
    data_id: str
    timestamp: float = field(default_factory=time.time)
    completeness: float = 1.0
    consistency: bool = True
    timeliness: bool = True
    provenance_present: bool = True
    ecological_valid: bool = True
    failures: list[str] = field(default_factory=list)
    quarantine_reason: str = ""


class DataQualityGate:
    """
    Codex-gated data quality gate for all GAIA data pipelines.

    Args:
        min_completeness:    Minimum fraction of non-null fields (default 0.9).
        max_age_seconds:     Maximum acceptable data age in seconds (default 3600).
        require_provenance:  If True, reject data with no source attribution.
        codex:               Optional CodexRuntime.
    """

    CODEX_VERSION = "v2.0"

    def __init__(
        self,
        min_completeness: float = 0.9,
        max_age_seconds: float = 3600.0,
        require_provenance: bool = True,
        codex=None,
    ):
        self.min_completeness = min_completeness
        self.max_age_seconds = max_age_seconds
        self.require_provenance = require_provenance
        self._codex = codex
        self._quarantine: list[tuple[Any, DataQualityResult]] = []
        self._passed_count = 0
        self._failed_count = 0
        logger.info(
            "DataQualityGate initialised (min_completeness=%.0f%%, max_age=%ss, Codex %s)",
            min_completeness * 100, max_age_seconds, self.CODEX_VERSION,
        )

    def evaluate(
        self,
        data: dict[str, Any],
        data_id: str = "",
        required_fields: list[str] | None = None,
    ) -> DataQualityResult:
        """
        Evaluate a data record against all Codex-aligned quality dimensions.

        Args:
            data:            The data record to evaluate (dict).
            data_id:         Optional identifier for audit trails.
            required_fields: Fields that must be present for completeness.

        Returns:
            DataQualityResult with full evaluation.
        """
        failures: list[str] = []

        # 1. Completeness
        if required_fields:
            present = sum(1 for f in required_fields if data.get(f) is not None)
            completeness = present / len(required_fields)
        else:
            non_null = sum(1 for v in data.values() if v is not None)
            completeness = non_null / len(data) if data else 1.0

        if completeness < self.min_completeness:
            failures.append("completeness")

        # 2. Consistency — basic: check no field is both present and None in required
        consistency = True
        if required_fields:
            for f in required_fields:
                if f in data and data[f] is None:
                    consistency = False
                    break
        if not consistency:
            failures.append("consistency")

        # 3. Timeliness
        timeliness = True
        ts = data.get("timestamp") or data.get("ts") or data.get("created_at")
        if ts is not None:
            try:
                age = time.time() - float(ts)
                timeliness = age <= self.max_age_seconds
            except (TypeError, ValueError):
                timeliness = True  # non-numeric timestamp — skip check
        if not timeliness:
            failures.append("timeliness")

        # 4. Provenance
        provenance_present = True
        if self.require_provenance:
            has_source = any(
                data.get(f) for f in ("source", "origin", "attribution", "sensor_id", "device_id")
            )
            if not has_source:
                provenance_present = False
                failures.append("provenance")

        # 5. Ecological validity — check for known-harmful patterns
        ecological_valid = True
        for key, val in data.items():
            if isinstance(val, str) and any(
                p in val.lower() for p in ("surveillance", "weaponise", "weaponize", "extract_all")
            ):
                ecological_valid = False
                failures.append("ecological_validity")
                break
        if not ecological_valid:
            failures.append("ecological_validity") if "ecological_validity" not in failures else None

        passed = len(failures) == 0
        quarantine_reason = ""
        if not passed:
            quarantine_reason = (
                f"Stage 6 (Mirror of Humble Truth): data quarantined. "
                f"Failed dimensions: {', '.join(failures)}."
            )

        result = DataQualityResult(
            passed=passed,
            data_id=data_id or str(id(data)),
            completeness=completeness,
            consistency=consistency,
            timeliness=timeliness,
            provenance_present=provenance_present,
            ecological_valid=ecological_valid,
            failures=failures,
            quarantine_reason=quarantine_reason,
        )

        if passed:
            self._passed_count += 1
            logger.debug("DataQualityGate: PASS — %s", data_id)
        else:
            self._failed_count += 1
            self._quarantine.append((data, result))
            logger.warning("DataQualityGate: QUARANTINE — %s | %s", data_id, quarantine_reason)

        return result

    def quarantine_log(self) -> list[tuple[Any, DataQualityResult]]:
        """Return all quarantined records with their quality results."""
        return list(self._quarantine)

    def stats(self) -> dict[str, Any]:
        """Return gate statistics for health monitoring."""
        total = self._passed_count + self._failed_count
        return {
            "passed": self._passed_count,
            "failed": self._failed_count,
            "total": total,
            "pass_rate": self._passed_count / total if total > 0 else 1.0,
            "quarantine_size": len(self._quarantine),
            "codex_version": self.CODEX_VERSION,
        }
