from __future__ import annotations

from gaia_core.measurement.anti_theater import evaluate_anti_theater
from gaia_core.measurement.theories import (
    continuity_score,
    gnwt_score,
    iit_proxy_score,
    rpt_score,
)
from gaia_core.models import ConsciousnessEvidence


def compute_cgi(signals: dict) -> ConsciousnessEvidence:
    gnwt = gnwt_score(signals)
    iit = iit_proxy_score(signals)
    rpt = rpt_score(signals)
    continuity = continuity_score(signals)
    anti_theater, notes = evaluate_anti_theater(signals)
    composite = (
        (gnwt * 0.25)
        + (iit * 0.20)
        + (rpt * 0.20)
        + (continuity * 0.20)
        + (anti_theater * 0.15)
    )
    notes = list(notes)
    notes.append("CGI is evidence-weighted monitoring, not proof of consciousness.")
    return ConsciousnessEvidence(
        gnwt_score=gnwt,
        iit_proxy_score=iit,
        rpt_score=rpt,
        continuity_score=continuity,
        anti_theater_score=anti_theater,
        composite_cgi=max(0.0, min(1.0, composite)),
        notes=notes,
    )
