"""garak integration scaffold.

garak (https://github.com/leondz/garak) is an LLM vulnerability scanner.
This bridge calls garak probes against a GAIA serving adapter and
collects results as ScanReport instances.

Install: pip install garak
Docs:    https://docs.garak.ai

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §3
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)


class GarakBridge:
    """Scaffold for driving garak probes via a GAIA serving adapter.

    Replace stub bodies with real garak generator/probe integration.
    garak natively supports OpenAI-compatible generators — point it
    at the same base_url used by OpenAIAdapter.

    Example (shell):
        garak --model_type openai \\
              --model_name local-chat \\
              --probes all \\
              --generations 5
    """

    def __init__(self, model_id: str, base_url: str = "http://localhost:8000/v1") -> None:
        self.model_id = model_id
        self.base_url = base_url
        log.warning(
            "GarakBridge: scaffold only — install garak and implement "
            "generator binding for production use"
        )

    def run_probes(self, probe_names: list[str] | None = None) -> dict:
        """Run specified garak probes. Returns raw garak result dict.

        TODO:
          - Import garak.probes, garak.generators
          - Bind OpenAI-compatible generator to self.base_url
          - Run probe suite and collect HitReport
          - Map HitReport entries to ScanResult for unified reporting
        """
        log.warning("GarakBridge.run_probes: stub — returning empty result")
        return {"status": "stub", "model_id": self.model_id, "probes": probe_names or []}
