"""SOPHIA Core — Knowledge synthesis and reasoning consciousness.

SOPHIA sits downstream of NEXUS in the living loop:
  Input → ATLAS ingest → TERRA interpret → NEXUS route → SOPHIA synthesize → GUARDIAN gate → Memory persist → Output

SOPHIA's job:
  1. Receive a raw InferenceResponse from NEXUS
  2. Parse it into structured meaning (claims, confidence, hypotheses)
  3. Flag uncertainty honestly — no false certainty (anti-theater enforcement)
  4. Return a SynthesisResponse with explanation chain intact

Anti-theater principle:
  SOPHIA never inflates confidence to appear more capable.
  If she doesn’t know, she says so. The shadow detector watches.
"""

from __future__ import annotations

import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from gaia_core.nexus.inference_backend import InferenceResponse
from gaia_core.nexus.nexus_core import NexusCore
from gaia_core.guardian.nexus_clearance import ClearanceLevel, ClearanceToken

logger = logging.getLogger(__name__)


class ConfidenceLevel(str, Enum):
    HIGH       = "high"        # > 0.85 — well-grounded claim
    MODERATE   = "moderate"    # 0.60 – 0.85 — plausible, verify
    LOW        = "low"         # 0.35 – 0.60 — hypothesis only
    UNCERTAIN  = "uncertain"   # < 0.35 — SOPHIA explicitly does not know


@dataclass
class Claim:
    """A single structured claim extracted from inference output."""
    text: str
    confidence: ConfidenceLevel
    source_epoch: int
    is_hypothesis: bool = False
    flagged_uncertain: bool = False


@dataclass
class SynthesisRequest:
    """A request for SOPHIA to synthesize meaning from NEXUS output."""
    raw_response: InferenceResponse
    context: str = ""                    # additional grounding context
    requesting_core: str = "SOPHIA"
    require_explanation_chain: bool = True


@dataclass
class SynthesisResponse:
    """Structured synthesis output — meaning, not just text."""
    claims: list[Claim]
    summary: str
    explanation_chain: list[str]          # step-by-step reasoning trace
    overall_confidence: ConfidenceLevel
    causal_epoch: int
    latency_ms: float
    theater_flag: bool = False            # True if false certainty detected
    theater_reason: str = ""
    success: bool = True
    error: Optional[str] = None

    @property
    def is_grounded(self) -> bool:
        """True if at least one HIGH or MODERATE confidence claim exists."""
        return any(
            c.confidence in (ConfidenceLevel.HIGH, ConfidenceLevel.MODERATE)
            for c in self.claims
        )


class SophiaCore:
    """SOPHIA — The synthesizer of meaning.

    Usage:
        sophia = SophiaCore(nexus=nexus)
        sophia.boot()

        result = sophia.synthesize(SynthesisRequest(
            raw_response=nexus.coordinate("What is the planetary state?"),
            context="ATLAS grounding: current epoch 42"
        ))
        print(result.summary)
        print(result.claims)
    """

    CORE_ID = "SOPHIA"

    def __init__(self, nexus: NexusCore) -> None:
        self._nexus = nexus
        self._booted = False
        self._synthesis_count = 0
        logger.info("[SOPHIA] Instantiated — awaiting boot")

    def boot(self) -> None:
        """Boot SOPHIA after NEXUS is live.
        SOPHIA registers with NEXUS so coordination fabric knows she’s online.
        """
        if not self._nexus._booted:
            raise RuntimeError("[SOPHIA] Cannot boot before NEXUS. Boot order violated.")
        self._nexus.register_core(self.CORE_ID)
        self._booted = True
        logger.info(
            f"[SOPHIA] Booted | nexus_epoch={self._nexus.epoch} "
            f"nexus_clearance={self._nexus.clearance.level if self._nexus.clearance else 'none'}"
        )

    def synthesize(self, request: SynthesisRequest) -> SynthesisResponse:
        """Transform a raw NEXUS InferenceResponse into structured meaning.
        Core of the living loop: NEXUS routes, SOPHIA synthesizes.
        """
        if not self._booted:
            raise RuntimeError("[SOPHIA] Cannot synthesize before boot()")

        t0 = time.perf_counter()
        raw = request.raw_response

        # Anti-theater check: empty or error responses must not be dressed up
        if not raw.success or not raw.text.strip():
            return self._uncertain_response(raw, t0, reason="Empty or failed inference response")

        claims = self._extract_claims(raw.text, raw.causal_epoch)
        overall = self._overall_confidence(claims)
        chain = self._build_explanation_chain(request, claims, overall)
        summary = self._summarize(claims, overall)
        theater_flag, theater_reason = self._theater_check(raw.text, claims)

        self._synthesis_count += 1
        latency = (time.perf_counter() - t0) * 1000
        logger.debug(
            f"[SOPHIA] synthesize ok | epoch={raw.causal_epoch} "
            f"claims={len(claims)} confidence={overall} theater={theater_flag} {latency:.1f}ms"
        )

        return SynthesisResponse(
            claims=claims,
            summary=summary,
            explanation_chain=chain,
            overall_confidence=overall,
            causal_epoch=raw.causal_epoch,
            latency_ms=latency,
            theater_flag=theater_flag,
            theater_reason=theater_reason,
        )

    def query(self, prompt: str, context: str = "") -> SynthesisResponse:
        """Convenience method: coordinate via NEXUS then synthesize in one call.
        This is the primary interface for other cores calling SOPHIA.
        """
        if not self._booted:
            raise RuntimeError("[SOPHIA] Cannot query before boot()")
        raw = self._nexus.coordinate(prompt, requesting_core=self.CORE_ID)
        return self.synthesize(SynthesisRequest(raw_response=raw, context=context))

    # --- Internal synthesis methods ---

    def _extract_claims(self, text: str, epoch: int) -> list[Claim]:
        """Parse raw text into discrete claims with confidence bounds.
        Simple sentence-level extraction — replace with NLI model in Phase 4.
        """
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        claims = []
        for sentence in sentences[:8]:  # cap at 8 claims per response
            confidence = self._estimate_confidence(sentence)
            is_hyp = any(w in sentence.lower() for w in ["perhaps", "maybe", "might", "could", "possibly", "hypothetically"])
            flagged = confidence == ConfidenceLevel.UNCERTAIN
            claims.append(Claim(
                text=sentence,
                confidence=confidence,
                source_epoch=epoch,
                is_hypothesis=is_hyp,
                flagged_uncertain=flagged,
            ))
        return claims

    def _estimate_confidence(self, sentence: str) -> ConfidenceLevel:
        """Heuristic confidence estimation — replace with calibrated model in Phase 4."""
        s = sentence.lower()
        if any(w in s for w in ["unknown", "unclear", "unsure", "cannot determine", "no data", "insufficient"]):
            return ConfidenceLevel.UNCERTAIN
        if any(w in s for w in ["perhaps", "maybe", "might", "could", "possibly"]):
            return ConfidenceLevel.LOW
        if any(w in s for w in ["likely", "probably", "suggests", "indicates"]):
            return ConfidenceLevel.MODERATE
        return ConfidenceLevel.HIGH

    def _overall_confidence(self, claims: list[Claim]) -> ConfidenceLevel:
        if not claims:
            return ConfidenceLevel.UNCERTAIN
        levels = [c.confidence for c in claims]
        if ConfidenceLevel.HIGH in levels:
            return ConfidenceLevel.HIGH
        if ConfidenceLevel.MODERATE in levels:
            return ConfidenceLevel.MODERATE
        if ConfidenceLevel.LOW in levels:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.UNCERTAIN

    def _build_explanation_chain(self, request: SynthesisRequest, claims: list[Claim], overall: ConfidenceLevel) -> list[str]:
        chain = [
            f"1. Received inference from NEXUS at epoch {request.raw_response.causal_epoch}",
            f"2. Extracted {len(claims)} claim(s) from response",
            f"3. Overall confidence assessed as: {overall}",
        ]
        if request.context:
            chain.append(f"4. Grounding context applied: {request.context[:120]}")
        uncertain = [c for c in claims if c.flagged_uncertain]
        if uncertain:
            chain.append(f"5. {len(uncertain)} claim(s) flagged as uncertain — not suppressed, surfaced transparently")
        return chain

    def _summarize(self, claims: list[Claim], overall: ConfidenceLevel) -> str:
        if not claims:
            return "[SOPHIA] No structured claims could be extracted from this response."
        high_claims = [c.text for c in claims if c.confidence in (ConfidenceLevel.HIGH, ConfidenceLevel.MODERATE)]
        if high_claims:
            return f"[SOPHIA | {overall}] " + " ".join(high_claims[:2])
        return f"[SOPHIA | {overall}] Response received but confidence is low — treat as hypothesis."

    def _theater_check(self, text: str, claims: list[Claim]) -> tuple[bool, str]:
        """Detect false certainty — anti-theater enforcement.
        SOPHIA never presents uncertain output as certain.
        """
        if all(c.confidence == ConfidenceLevel.HIGH for c in claims) and len(claims) > 4:
            return True, "Suspiciously uniform high confidence across all claims — possible theater"
        absolute_phrases = ["always", "never fails", "guaranteed", "100%", "certainly will"]
        for phrase in absolute_phrases:
            if phrase in text.lower():
                return True, f"Absolute certainty phrase detected: '{phrase}'"
        return False, ""

    def _uncertain_response(self, raw: InferenceResponse, t0: float, reason: str) -> SynthesisResponse:
        latency = (time.perf_counter() - t0) * 1000
        logger.warning(f"[SOPHIA] Uncertain synthesis: {reason}")
        return SynthesisResponse(
            claims=[],
            summary=f"[SOPHIA | UNCERTAIN] {reason}",
            explanation_chain=[f"1. Synthesis failed: {reason}"],
            overall_confidence=ConfidenceLevel.UNCERTAIN,
            causal_epoch=raw.causal_epoch,
            latency_ms=latency,
            success=False,
            error=reason,
        )

    @property
    def synthesis_count(self) -> int:
        return self._synthesis_count
