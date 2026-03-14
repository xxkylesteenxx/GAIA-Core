"""GAIA Persistent Memory — causal event log + morphic checkpoints.

Nothing is forgotten. Nothing is revised. Only appended.
GAIA wakes up knowing who she is and what she has experienced.
"""

from .memory_manager import MemoryManager, CausalEvent, CheckpointManifest

__all__ = ["MemoryManager", "CausalEvent", "CheckpointManifest"]
__version__ = "0.1.0"
