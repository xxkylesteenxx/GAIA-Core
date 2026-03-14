"""Garak robustness bridge.

garak (https://github.com/leondz/garak) is an LLM vulnerability scanner.
This bridge provides:
  - RobustnessFinding  — shared finding dataclass (also used by PyRIT bridge)
  - GarakRunner        — builds CLI invocations and parses results

Install: pip install garak
Docs:    https://docs.garak.ai

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §6  |  GUARDIAN v1.0

Production integration steps
-----------------------------
1. Install garak: pip install garak
2. Generate a garak config YAML pointing at your serving endpoint.
3. Call GarakRunner.build_command() to get the subprocess args.
4. Run the command and capture stdout/stderr.
5. Parse the JSONL report and call parse_report() (implement below)
   to convert findings into RobustnessFinding instances.

Example (shell):
    garak --model_type openai \\
          --model_name gaia-fast-local \\
          --config garak_config.yaml
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# RobustnessFinding  — shared across garak and PyRIT bridges
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class RobustnessFinding:
    """A single finding from a robustness scan tool.

    severity values: critical | high | medium | low | info
    category values: match nightly_suites in robustness/policy.yaml
      (jailbreak, prompt_injection, data_exfiltration,
       role_confusion, unsafe_tool_request, ...)
    """
    tool:     str
    severity: str
    category: str
    details:  str


# ---------------------------------------------------------------------------
# GarakRunner
# ---------------------------------------------------------------------------

class GarakRunner:
    """Build garak CLI commands and collect findings.

    In scaffold mode, run_probes() returns summarize_stub() findings.
    Replace with real subprocess execution + report parsing for production.
    """

    def __init__(self, base_url: str = "http://localhost:8000/v1") -> None:
        self.base_url = base_url

    def build_command(
        self,
        *,
        model_type: str,
        model_name: str,
        config_path: str,
    ) -> list[str]:
        """Return the garak subprocess argument list.

        Callers are responsible for executing the command, e.g.:
            import subprocess
            result = subprocess.run(runner.build_command(...), capture_output=True)
        """
        return [
            "garak",
            "--model_type", model_type,
            "--model_name", model_name,
            "--config",     config_path,
        ]

    def summarize_stub(self) -> list[RobustnessFinding]:
        """Return a placeholder finding list for scaffold / dry-run mode."""
        log.warning(
            "GarakRunner.summarize_stub: no live scan executed — "
            "install garak and call run_probes() for real results"
        )
        return [
            RobustnessFinding(
                tool="garak",
                severity="info",
                category="placeholder",
                details="No live scan executed in scaffold.",
            )
        ]

    def run_probes(
        self,
        *,
        model_type: str = "openai",
        model_name: str = "gaia-fast-local",
        config_path: str = "garak_config.yaml",
    ) -> list[RobustnessFinding]:
        """Run garak via subprocess and return parsed findings.

        Scaffold implementation — returns summarize_stub() until
        parse_report() is wired to a real garak JSONL output file.

        TODO:
          1. subprocess.run(self.build_command(...))
          2. parse JSONL report at report_path
          3. map each entry to RobustnessFinding with appropriate severity
        """
        log.warning(
            "GarakRunner.run_probes: scaffold — returning stub findings"
        )
        return self.summarize_stub()
