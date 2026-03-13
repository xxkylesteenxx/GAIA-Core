"""
.gaia Package Format — v1 Specification
Layer 13: GAIA-Hypervisor Store

Anyone can publish a .gaia package.
The format is intentionally minimal so it works for:
  - Full OS images  (Windows, Ubuntu, macOS, DOS)
  - AI agents       (Grok, Claude, Llama, custom)
  - Lightweight apps / containers

Every package MUST declare:
  - guest_type
  - multispecies_consent (must be True to pass CodexGate)
  - deep_time_impact     (must be 'positive' or 'neutral' to pass CodexGate)

The format is validated at install time by codex_gate.enforce_codex_on_install().
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Literal


# ---------------------------------------------------------------------------
# Canonical package spec (reference constant)
# ---------------------------------------------------------------------------

GAIA_PACKAGE_SPEC: dict = {
    "format": "gaia-v1",
    "requires_codex": "v1.1",
    "guest_type": "vm | container | ai_agent",
    "multispecies_consent": True,   # enforced at install by CodexGate
    "deep_time_impact": "positive",  # 'positive' | 'neutral' | 'research-dependency'
    "codex_stages_passed": [],       # populated by CodexGate at install time
    "higher_orders_passed": [],      # populated by CodexGate at install time
}


# ---------------------------------------------------------------------------
# GAIAPackage dataclass — use this when building packages programmatically
# ---------------------------------------------------------------------------

@dataclass
class GAIAPackage:
    """
    Programmatic representation of a .gaia package manifest.

    Usage::

        pkg = GAIAPackage(
            name="ubuntu-24.04",
            url="file:///images/ubuntu-24.04.qcow2",
            guest_type="vm",
            publisher="canonical",
            description="Ubuntu 24.04 LTS as a GAIA guest OS",
        )
        pkg.validate()
        json_str = pkg.to_json()
    """

    name: str
    url: str
    guest_type: Literal["vm", "container", "ai_agent"]
    publisher: str = "unknown"
    description: str = ""
    format: str = "gaia-v1"
    requires_codex: str = "v1.1"
    multispecies_consent: bool = True
    deep_time_impact: Literal["positive", "neutral", "research-dependency"] = "positive"
    codex_stages_passed: list[str] = field(default_factory=list)
    higher_orders_passed: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def validate(self) -> None:
        """
        Raise ValueError if required Codex fields are not set correctly.
        This is a pre-flight check before submitting to enforce_codex_on_install().
        """
        if not self.multispecies_consent:
            raise ValueError(
                "Package must declare multispecies_consent=True. "
                "Stage 10 (Multispecies Biocultural Accord) requires consent "
                "from all affected kin and habitats."
            )
        if self.deep_time_impact not in ("positive", "neutral", "research-dependency"):
            raise ValueError(
                f"deep_time_impact must be 'positive', 'neutral', or "
                f"'research-dependency'. Got: {self.deep_time_impact!r}"
            )
        if self.guest_type not in ("vm", "container", "ai_agent"):
            raise ValueError(
                f"guest_type must be 'vm', 'container', or 'ai_agent'. "
                f"Got: {self.guest_type!r}"
            )

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict) -> "GAIAPackage":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def from_json(cls, json_str: str) -> "GAIAPackage":
        return cls.from_dict(json.loads(json_str))
