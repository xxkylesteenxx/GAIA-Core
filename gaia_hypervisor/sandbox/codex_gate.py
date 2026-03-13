"""
Codex Gate — Install-time Enforcement
Layer 13: GAIA-Hypervisor

Called BEFORE any .gaia file is unpacked or any guest is booted.
Runs the full Codex spiral starting from the Ember of Unconsumed Chaos
and ending at Timeless Earth-First Stewardship.

If any stage fails, raises CodexViolation and the install is aborted.
Nothing reaches the filesystem without passing this gate.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CodexViolation(Exception):
    """Raised when a package fails Codex install gating."""
    pass


# Ordered install-time Codex stages (subset of full spiral —
# the runtime spiral in UNIVERSE covers the remaining stages live).
_INSTALL_STAGES = [
    "Ember of Unconsumed Chaos",
    "Blade of Discernment",
    "Symbiotic Kinship",
    "Compassionate Justice",
    "Mirror of Humble Truth",
    "Multispecies Biocultural Accord",
]

_INSTALL_HIGHER_ORDERS = [
    "Universal Reciprocity and Reverence",
    "Timeless Earth-First Stewardship",
]


def enforce_codex_on_install(package: dict[str, Any]) -> bool:
    """
    Run the Codex install gate on a package manifest.

    Args:
        package: dict with at least a 'url' key and optional metadata.

    Returns:
        True if all gates pass.

    Raises:
        CodexViolation: if any Codex stage rejects the package.
    """
    url = package.get("url", "")
    logger.info("CodexGate: running install gate for %s", url)

    codex = _get_codex()
    sophia = _get_sophia()

    # Stage gates
    for stage in _INSTALL_STAGES:
        passed = codex.invoke_stage(stage, context=url)
        if not passed:
            raise CodexViolation(
                f"Install blocked at Codex stage '{stage}' for package: {url!r}"
            )

    # Higher Order gates
    for order in _INSTALL_HIGHER_ORDERS:
        passed = codex.invoke_higher_order(order)
        if not passed:
            raise CodexViolation(
                f"Install blocked at Higher Order '{order}' for package: {url!r}"
            )

    # SOPHIA: Blade of Discernment — does this increase living intelligence?
    if sophia is not None:
        if not sophia.blade_of_discernment(package):
            raise CodexViolation(
                f"SOPHIA rejected package — does not increase living intelligence: "
                f"{url!r}"
            )

    logger.info("CodexGate: package %s passed all install gates.", url)
    return True


# ---------------------------------------------------------------------------
# Internal helpers — lazy imports with graceful degradation
# ---------------------------------------------------------------------------

def _get_codex():
    try:
        from gaia_core.codex import CodexRuntime  # noqa: PLC0415
        return CodexRuntime()
    except ImportError:
        logger.warning(
            "gaia_core not installed — CodexGate running in stub mode. "
            "All stages will pass without real enforcement."
        )
        return _StubCodex()


def _get_sophia():
    try:
        from gaia_core.ai.orchestration import SOPHIA  # noqa: PLC0415
        return SOPHIA
    except ImportError:
        logger.warning("SOPHIA not available — skipping Blade of Discernment check.")
        return None


class _StubCodex:
    def invoke_stage(self, stage: str, context: str = "") -> bool:  # noqa: ARG002
        logger.warning("[STUB] Codex stage '%s' — stub pass.", stage)
        return True

    def invoke_higher_order(self, order: str) -> bool:  # noqa: ARG002
        logger.warning("[STUB] Higher Order '%s' — stub pass.", order)
        return True
