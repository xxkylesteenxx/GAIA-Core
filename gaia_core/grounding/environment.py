from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from gaia_core.models import EnvironmentalObservation, ObservationSourceClass


def classify_freshness(latency_seconds: float) -> str:
    if latency_seconds < 300:
        return "URT"
    if latency_seconds < 3600:
        return "RT"
    if latency_seconds < 3 * 3600:
        return "NRT"
    if latency_seconds < 24 * 3600:
        return "LL"
    if latency_seconds < 4 * 24 * 3600:
        return "EXP"
    return "STD"


def normalize_observation(
    source_id: str,
    domain: str,
    payload: Dict[str, Any],
    source_class: ObservationSourceClass,
    observed_at: datetime,
    ingest_at: datetime | None = None,
    quality_score: float = 0.8,
    adversarial_suspicion: float = 0.0,
) -> EnvironmentalObservation:
    ingest_at = ingest_at or datetime.now(timezone.utc)
    latency_seconds = max(0.0, (ingest_at - observed_at).total_seconds())
    return EnvironmentalObservation(
        source_id=source_id,
        domain=domain,
        observed_at=observed_at,
        ingest_at=ingest_at,
        payload=payload,
        source_class=source_class,
        quality_score=quality_score,
        latency_seconds=latency_seconds,
        freshness_class=classify_freshness(latency_seconds),
        adversarial_suspicion=adversarial_suspicion,
    )
