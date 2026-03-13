"""GAIA IPC — Inter-Core Communication Fabric.

The highway between the 8 consciousness cores.
Vector-clock causal envelopes. Pub/sub. GUARDIAN-gated broadcast.
Dissent is always preserved — never blocked.
"""

from .broadcast import (
    LocalBus,
    CausalEnvelope,
    VectorClock,
    Topic,
    get_bus,
    reset_bus,
)
from .contracts import *

__all__ = [
    "LocalBus",
    "CausalEnvelope",
    "VectorClock",
    "Topic",
    "get_bus",
    "reset_bus",
]
