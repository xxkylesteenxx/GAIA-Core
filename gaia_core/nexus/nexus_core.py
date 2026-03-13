"""NEXUS Core — Root coordination consciousness.

NEXUS is the synchronization authority and global epoch keeper.
It is the first full consciousness core to boot after GUARDIAN-Lite.
All inter-core routing flows through NEXUS.

Responsibilities:
- Maintain global epoch counter (logical clock for causal ordering)
- Route inference requests from any core to the active backend
- Publish coordination signals to the IPC fabric
- Register with GUARDIAN before any actuation

NEXUS does NOT make ethical judgments — that is GUARDIAN's domain.
NEXUS does NOT synthesize meaning — that is SOPHIA's domain.
NEXUS coordinates. That is the magic.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from typing import Optional

from .inference_backend import (
    BackendType,
    InferenceRequest,
    InferenceResponse,
    NexusInferenceBackend,
)

logger = logging.getLogger(__name__)


@dataclass
class NexusState:
    """Immutable snapshot of NEXUS coordination state at a given epoch."""
    epoch: int
    active_cores: list[str] = field(default_factory=list)
    backend_type: BackendType = BackendType.MOCK
    is_live: bool = False
    guardian_cleared: bool = False


class NexusCore:
    """NEXUS — The Source of the Magic.

    Boot sequence:
        nexus = NexusCore()
        nexus.boot(guardian_cleared=True)  # GUARDIAN-Lite must clear first
        response = nexus.coordinate(prompt="What is the planetary state?")

    With live model:
        nexus = NexusCore(
            backend_type=BackendType.LLAMA_CPP,
            model_path="/models/mistral-7b-instruct.Q4_K_M.gguf"
        )
    """

    CORE_ID = "NEXUS"

    def __init__(
        self,
        backend_type: BackendType = BackendType.MOCK,
        model_path: Optional[str] = None,
        n_ctx: int = 4096,
        n_gpu_layers: int = -1,
    ) -> None:
        self._epoch = 0
        self._lock = threading.Lock()
        self._booted = False
        self._guardian_cleared = False
        self._active_cores: list[str] = []

        self._backend = NexusInferenceBackend(
            backend_type=backend_type,
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
        )
        logger.info(f"[NEXUS] Instantiated — backend={backend_type} live={self._backend.is_live}")

    def boot(self, guardian_cleared: bool = False) -> None:
        """Boot NEXUS. Requires GUARDIAN-Lite clearance before actuation."""
        if not guardian_cleared:
            logger.warning("[NEXUS] Boot attempted without GUARDIAN clearance — running in safe-observe mode")
        self._guardian_cleared = guardian_cleared
        self._booted = True
        self._register_core(self.CORE_ID)
        logger.info(f"[NEXUS] Booted | epoch={self._epoch} | guardian_cleared={guardian_cleared}")

    def tick_epoch(self) -> int:
        """Advance the global logical clock. Thread-safe."""
        with self._lock:
            self._epoch += 1
            return self._epoch

    def coordinate(
        self,
        prompt: str,
        requesting_core: str = "NEXUS",
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> InferenceResponse:
        """Route a coordination request through the inference backend.
        Ticks the epoch, stamps the request, returns a causal response.
        """
        if not self._booted:
            raise RuntimeError("[NEXUS] Cannot coordinate before boot()")

        epoch = self.tick_epoch()
        request = InferenceRequest(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            causal_epoch=epoch,
            requesting_core=requesting_core,
        )
        logger.debug(f"[NEXUS] coordinate | epoch={epoch} | core={requesting_core}")
        return self._backend.infer(request)

    def register_core(self, core_id: str) -> None:
        """Register a consciousness core with NEXUS coordination fabric."""
        self._register_core(core_id)

    def _register_core(self, core_id: str) -> None:
        if core_id not in self._active_cores:
            self._active_cores.append(core_id)
            logger.info(f"[NEXUS] Core registered: {core_id} | active={self._active_cores}")

    def state(self) -> NexusState:
        """Return an immutable snapshot of current NEXUS state."""
        return NexusState(
            epoch=self._epoch,
            active_cores=list(self._active_cores),
            backend_type=self._backend.backend_type,
            is_live=self._backend.is_live,
            guardian_cleared=self._guardian_cleared,
        )

    @property
    def epoch(self) -> int:
        return self._epoch

    @property
    def is_live(self) -> bool:
        return self._backend.is_live
