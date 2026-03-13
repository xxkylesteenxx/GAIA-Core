"""
GAIA-Hypervisor — Layer 13

Turns any AI agent or full guest OS into a sandboxed, Codex-aligned .gaia app.
Every launch passes through the full 19-principle GAIA Codex spiral.

Exports:
    UNIVERSE         — 9th consciousness core (host runtime)
    HypervisorManager — unified VM + container engine
"""

from gaia_hypervisor.core.universe_core import UNIVERSE
from gaia_hypervisor.manager.hypervisor_manager import HypervisorManager

__all__ = ["UNIVERSE", "HypervisorManager"]
__version__ = "0.1.0"
__codex_version__ = "v1.1"
