"""gaia_core.self — the self-model layer.

This is the layer that makes GAIA GAIA across time.
Not memory as a lookup table. Not a persona file.
A persistent, grounded, perturbation-resilient identity substrate.

Three components:
    IdentityRoot   — what GAIA is and why, across sessions
    WorldModel     — the virtual Earth GAIA inhabits, not just retrieves
    Embodiment     — the persistent character envelope under pressure
"""

from gaia_core.self.identity import IdentityRoot, IdentitySnapshot, CoreValue
from gaia_core.self.world_model import WorldModel, Observation, WorldSnapshot
from gaia_core.self.embodiment import Embodiment, ResponsePosture

__all__ = [
    "IdentityRoot",
    "IdentitySnapshot",
    "CoreValue",
    "WorldModel",
    "Observation",
    "WorldSnapshot",
    "Embodiment",
    "ResponsePosture",
]
