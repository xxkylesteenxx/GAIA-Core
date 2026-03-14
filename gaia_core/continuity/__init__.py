"""GAIA Continuity Layer — identity, causal memory, checkpoints.

The continuity layer ensures GAIA persists across restarts.
Identity root is never lost. Events are never deleted.
Checkpoints are morphic snapshots, not discrete resets.
"""

from .causal_memory import CausalMemoryLog
from .checkpoints import CheckpointStore
from .identity import IdentityRoot

__all__ = ["CausalMemoryLog", "CheckpointStore", "IdentityRoot"]
