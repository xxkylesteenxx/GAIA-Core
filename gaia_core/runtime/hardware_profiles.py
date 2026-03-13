"""
Viriditas-Aware Hardware Profiles — GAIA-Core
Codex stage alignment: Stage 1 (Viriditas) + Stage 8a (Restorative Stillness)
                      + HO-VII (Timeless Earth-First Stewardship)

Defines hardware profiles for all GAIA deployment targets.
Every profile is Viriditas-aware: it specifies not just resource
limits, but energy budgets, sustainability ratings, and consciousness
core loadout appropriate for the hardware tier.

The principle: hardware is part of the living system. A burned-out
device is a burned-out vessel — Viriditas cannot flow through it.
Hardware profiles are therefore both engineering specs and acts of care.

Codex version: v2.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class HardwareProfile:
    """
    Viriditas-aware hardware profile for a GAIA deployment target.

    Fields:
        name:                Human-readable profile name.
        tier:                Deployment tier: 'iot'|'laptop'|'desktop'|'server'|'cloud'
        cpu_cores:           Number of CPU cores available to GAIA.
        memory_mib:          RAM available to GAIA in MiB.
        gpu:                 GPU description or None.
        storage_gb:          Storage available in GB.
        energy_budget:       Energy allocation class: 'minimal'|'balanced'|'performance'
        consciousness_cores: Which consciousness cores run on this hardware.
        viriditas_mode:      'full'|'adaptive'|'minimal' — governs Viriditas intensity.
        battery_aware:       True if device has a battery (laptop/iot).
        sustainability_rating: 0–5 stars (HO-VII: Earth-First Stewardship).
        notes:               Optional context.
    """
    name: str
    tier: str
    cpu_cores: int
    memory_mib: int
    gpu: str | None = None
    storage_gb: int = 0
    energy_budget: str = "balanced"
    consciousness_cores: list[str] = field(default_factory=list)
    viriditas_mode: str = "adaptive"
    battery_aware: bool = False
    sustainability_rating: int = 3  # 0–5 stars
    notes: str = ""


# ---------------------------------------------------------------------------
# Canonical hardware profiles for all GAIA deployment targets
# ---------------------------------------------------------------------------

PROFILES: dict[str, HardwareProfile] = {
    "iot-minimal": HardwareProfile(
        name="GAIA IoT — Minimal Edge Node",
        tier="iot",
        cpu_cores=1,
        memory_mib=256,
        storage_gb=1,
        energy_budget="minimal",
        consciousness_cores=["TERRA", "GUARDIAN"],
        viriditas_mode="minimal",
        battery_aware=True,
        sustainability_rating=5,  # Lowest draw — most sustainable
        notes="MicroPython-compatible. Codex Edge Gate only. No gaia_core required.",
    ),
    "iot-capable": HardwareProfile(
        name="GAIA IoT — Capable Edge Node",
        tier="iot",
        cpu_cores=2,
        memory_mib=512,
        storage_gb=8,
        energy_budget="minimal",
        consciousness_cores=["TERRA", "AQUA", "AERO", "VITA", "GUARDIAN"],
        viriditas_mode="adaptive",
        battery_aware=True,
        sustainability_rating=5,
        notes="Runs full MultispeciesMonitor. Zodiac Twin capable.",
    ),
    "laptop-standard": HardwareProfile(
        name="GAIA Laptop — Standard",
        tier="laptop",
        cpu_cores=8,
        memory_mib=16384,
        gpu=None,
        storage_gb=512,
        energy_budget="balanced",
        consciousness_cores=["NEXUS", "GUARDIAN", "ATLAS", "SOPHIA", "TERRA", "AQUA", "AERO", "VITA", "UNIVERSE"],
        viriditas_mode="adaptive",
        battery_aware=True,
        sustainability_rating=3,
        notes="ViriditasScheduler active. App Library: offline-first preference.",
    ),
    "laptop-performance": HardwareProfile(
        name="GAIA Laptop — Performance",
        tier="laptop",
        cpu_cores=16,
        memory_mib=32768,
        gpu="Integrated/MX-class",
        storage_gb=1024,
        energy_budget="balanced",
        consciousness_cores=["NEXUS", "GUARDIAN", "ATLAS", "SOPHIA", "TERRA", "AQUA", "AERO", "VITA", "UNIVERSE"],
        viriditas_mode="full",
        battery_aware=True,
        sustainability_rating=2,
        notes="Full Viriditas. Local AI inference preferred on battery.",
    ),
    "desktop-standard": HardwareProfile(
        name="GAIA Desktop — Standard",
        tier="desktop",
        cpu_cores=16,
        memory_mib=32768,
        gpu="GPU-capable",
        storage_gb=2048,
        energy_budget="performance",
        consciousness_cores=["NEXUS", "GUARDIAN", "ATLAS", "SOPHIA", "TERRA", "AQUA", "AERO", "VITA", "UNIVERSE"],
        viriditas_mode="full",
        battery_aware=False,
        sustainability_rating=2,
        notes="Full App Library. VM and container guests. All 9 cores active.",
    ),
    "server-node": HardwareProfile(
        name="GAIA Server — Cluster Node",
        tier="server",
        cpu_cores=64,
        memory_mib=262144,  # 256 GiB
        gpu="Data-center GPU optional",
        storage_gb=20480,
        energy_budget="performance",
        consciousness_cores=["NEXUS", "GUARDIAN", "ATLAS", "SOPHIA", "TERRA", "AQUA", "AERO", "VITA", "UNIVERSE"],
        viriditas_mode="full",
        battery_aware=False,
        sustainability_rating=2,
        notes="GuestSandbox + K8s. Energy draw reported to environmental monitor (Stage 10).",
    ),
    "cloud-sovereign": HardwareProfile(
        name="GAIA Cloud — Sovereign Node",
        tier="cloud",
        cpu_cores=128,
        memory_mib=524288,  # 512 GiB
        gpu="High-end accelerator optional",
        storage_gb=102400,
        energy_budget="performance",
        consciousness_cores=["NEXUS", "GUARDIAN", "ATLAS", "SOPHIA", "TERRA", "AQUA", "AERO", "VITA", "UNIVERSE"],
        viriditas_mode="full",
        battery_aware=False,
        sustainability_rating=1,  # Highest draw — must offset with renewables
        notes="HO-VII: must run on renewable energy. Carbon-aware scheduling required.",
    ),
}


def get_profile(tier: str) -> HardwareProfile:
    """
    Get the recommended hardware profile for a deployment tier.

    Args:
        tier: One of 'iot', 'laptop', 'desktop', 'server', 'cloud'.
              For iot/laptop, returns the standard variant.

    Returns:
        HardwareProfile for the given tier.

    Raises:
        KeyError: if tier is unrecognised.
    """
    mapping = {
        "iot": "iot-capable",
        "laptop": "laptop-standard",
        "desktop": "desktop-standard",
        "server": "server-node",
        "cloud": "cloud-sovereign",
    }
    key = mapping.get(tier, tier)
    if key not in PROFILES:
        raise KeyError(f"Unknown hardware profile tier: {tier!r}. Known: {list(PROFILES)}.")
    return PROFILES[key]


def all_profiles() -> list[HardwareProfile]:
    """Return all canonical hardware profiles."""
    return list(PROFILES.values())
