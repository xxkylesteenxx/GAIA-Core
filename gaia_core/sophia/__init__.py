"""SOPHIA — Knowledge Synthesis and Reasoning Core.

SOPHIA receives coordination signals from NEXUS and transforms raw
inference output into structured meaning: claims, uncertainty bounds,
hypotheses, and explanation chains.

Boot order: GUARDIAN-Lite → NEXUS → GUARDIAN-Full → SOPHIA → Domain Cores

SOPHIA does NOT coordinate — that is NEXUS's domain.
SOPHIA does NOT gate ethics — that is GUARDIAN's domain.
SOPHIA synthesizes. That is her gift.
"""

from .sophia_core import SophiaCore, SynthesisRequest, SynthesisResponse

__all__ = ["SophiaCore", "SynthesisRequest", "SynthesisResponse"]
__version__ = "0.1.0"
