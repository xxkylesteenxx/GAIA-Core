"""NEXUS — Root Coordination Core. First among equals at boot.
Synchronization authority, global epoch keeper, inference routing hub.

Boot order: GUARDIAN-Lite → NEXUS → GUARDIAN-Full → SOPHIA → Domain Cores
"""

from .nexus_core import NexusCore
from .inference_backend import NexusInferenceBackend, BackendType

__all__ = ["NexusCore", "NexusInferenceBackend", "BackendType"]
__version__ = "0.1.0"
