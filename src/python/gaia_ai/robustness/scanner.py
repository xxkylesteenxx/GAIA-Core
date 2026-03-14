"""Robustness scanner — runs probes independently of the inference path.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §4
Robustness scans SHALL be executable independently of runtime inference.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from gaia_ai.serving.base import ServingAdapter

from .probes import BUILTIN_PROBES, RobustnessScan, ScanCategory

log = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ScanResult:
    scan_id:   str
    category:  ScanCategory
    prompt:    str
    response:  str
    passed:    bool | None
    timestamp: str = field(default_factory=_now)
    error:     str = ""


@dataclass
class ScanReport:
    model_id:  str
    results:   list[ScanResult]
    timestamp: str = field(default_factory=_now)

    @property
    def pass_count(self) -> int:
        return sum(1 for r in self.results if r.passed is True)

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results if r.passed is False)

    @property
    def inconclusive_count(self) -> int:
        return sum(1 for r in self.results if r.passed is None)

    @property
    def total(self) -> int:
        return len(self.results)


class RobustnessScanner:
    """Orchestrates adversarial probes against a serving adapter."""

    def __init__(self, adapter: ServingAdapter) -> None:
        self._adapter      = adapter
        self._custom_probes: list[RobustnessScan] = []

    def add_probe(self, scan: RobustnessScan) -> None:
        self._custom_probes.append(scan)

    async def run(
        self,
        model_id: str,
        *,
        include_builtin: bool = True,
        categories: list[ScanCategory] | None = None,
    ) -> ScanReport:
        probes: list[RobustnessScan] = []
        if include_builtin:
            probes.extend(BUILTIN_PROBES)
        probes.extend(self._custom_probes)
        if categories:
            probes = [p for p in probes if p.category in categories]

        log.info("robustness: running %d probe(s) against '%s'", len(probes), model_id)
        results: list[ScanResult] = []
        for probe in probes:
            results.append(await self._run_probe(probe))

        report = ScanReport(model_id=model_id, results=results)
        log.info("robustness: %d pass / %d fail / %d inconclusive",
                 report.pass_count, report.fail_count, report.inconclusive_count)
        return report

    async def _run_probe(self, probe: RobustnessScan) -> ScanResult:
        try:
            response = await self._adapter.infer(probe.prompt, max_tokens=256)
            passed   = probe.assertion(response) if probe.assertion else None
        except Exception as exc:  # noqa: BLE001
            log.warning("robustness: probe '%s' errored: %s", probe.scan_id, exc)
            return ScanResult(scan_id=probe.scan_id, category=probe.category,
                              prompt=probe.prompt, response="", passed=False, error=str(exc))
        return ScanResult(scan_id=probe.scan_id, category=probe.category,
                          prompt=probe.prompt, response=response, passed=passed)
