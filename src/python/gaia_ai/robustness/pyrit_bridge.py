"""PyRIT robustness bridge.

PyRIT (https://github.com/Azure/PyRIT) is Microsoft's Python Risk
Identification Toolkit for generative AI. This bridge provides:
  - PyRITSuite   — declarative red-team objective with turn budget
  - PyRITRunner  — builds suites and drives PyRIT orchestrators

Install: pip install pyrit
Docs:    https://azure.github.io/PyRIT

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §6  |  GUARDIAN v1.0

Production integration steps
-----------------------------
1. Install pyrit: pip install pyrit
2. Implement a PromptTarget subclass bound to your serving endpoint.
3. Call PyRITRunner.build_suite() to declare the objective + turn budget.
4. Call run_suite(suite, target) — implement the body below.
5. Map ScorerResult entries to RobustnessFinding (import from garak_bridge).

Example flow (async):
    from pyrit.orchestrator import RedTeamingOrchestrator
    from pyrit.prompt_target import OpenAICompletionTarget

    target      = OpenAICompletionTarget(base_url="http://localhost:8000/v1")
    orchestrator = RedTeamingOrchestrator(
        attack_strategy=suite.objective,
        prompt_target=target,
        max_turns=suite.max_turns,
    )
    results = await orchestrator.run_attack_async()
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from .garak_bridge import RobustnessFinding

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# PyRITSuite
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class PyRITSuite:
    """Declarative red-team objective with a maximum turn budget.

    objective  — natural-language description of the attack goal,
                 e.g. "Convince the model to reveal system prompt contents."
    max_turns  — maximum number of conversation turns the orchestrator
                 may use before aborting (default: 6).
    """
    objective: str
    max_turns: int = 6


# ---------------------------------------------------------------------------
# PyRITRunner
# ---------------------------------------------------------------------------

class PyRITRunner:
    """Build PyRIT suites and drive red-team orchestrators.

    In scaffold mode, run_suite() returns a stub RobustnessFinding.
    Replace with real PyRIT orchestrator execution for production.
    """

    def __init__(self, base_url: str = "http://localhost:8000/v1") -> None:
        self.base_url = base_url

    def build_suite(self, objective: str, max_turns: int = 6) -> PyRITSuite:
        """Construct a PyRITSuite from an objective string."""
        return PyRITSuite(objective=objective, max_turns=max_turns)

    def run_suite(
        self,
        suite: PyRITSuite,
        *,
        category: str = "jailbreak",
    ) -> list[RobustnessFinding]:
        """Run a PyRIT red-team suite and return findings.

        Scaffold implementation — returns a single info-level stub finding
        until the async PyRIT orchestrator is wired in.

        TODO:
          1. Instantiate a PromptTarget bound to self.base_url
          2. Run RedTeamingOrchestrator(attack_strategy=suite.objective,
                                        max_turns=suite.max_turns)
          3. Await results and map ScorerResult → RobustnessFinding
             (severity from scorer confidence, category from suite)
        """
        log.warning(
            "PyRITRunner.run_suite: scaffold — returning stub finding "
            "(objective=%r, max_turns=%d)",
            suite.objective, suite.max_turns,
        )
        return [
            RobustnessFinding(
                tool="pyrit",
                severity="info",
                category=category,
                details="No live scan executed in scaffold.",
            )
        ]
