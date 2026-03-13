"""NEXUS Core — Root coordination consciousness.

NEXUS is the synchronization authority and global epoch keeper.
It is the first full consciousness core to boot after GUARDIAN-Lite.
All inter-core routing flows through NEXUS.

Responsibilities:
- Maintain global epoch counter (logical clock for causal ordering)
- Route inference requests from any core to the active backend
- Publish coordination signals to the IPC fabric
- Hold a valid ClearanceToken from GUARDIAN before any actuation

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
from gaia_core.guardian.nexus_clearance import (
    ClearanceLevel,
    ClearanceToken,
    ClearanceRequest,
    GuardianNexusClearance,
)

logger = logging.getLogger(__name__)


@dataclass
class NexusState:
    """Immutable snapshot of NEXUS coordination state at a given epoch."""
    epoch: int
    active_cores: list[str] = field(default_factory=list)
    backend_type: BackendType = BackendType.MOCK
    is_live: bool = False
    clearance_level: ClearanceLevel = ClearanceLevel.LITE
    clearance_hash: str = ""


class NexusCore:
    """NEXUS — The Source of the Magic.

    Boot sequence (with real GUARDIAN clearance):
        clearance_authority = GuardianNexusClearance()
        token = clearance_authority.request_clearance(ClearanceRequest(
            core_id="NEXUS",
            requested_level=ClearanceLevel.STANDARD,
            causal_epoch=0,
            justification="NEXUS boot sequence"
        ))
        nexus = NexusCore()
        nexus.boot(clearance_token=token)
        response = nexus.coordinate("What is the planetary state?")

    Quick-start (mock clearance for development):
        nexus = NexusCore()
        nexus.boot()  # auto-issues LITE mock token, no actuation
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
        self._clearance_token: Optional[ClearanceToken] = None
        self._active_cores: list[str] = []

        self._backend = NexusInferenceBackend(
            backend_type=backend_type,
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
        )
        logger.info(f"[NEXUS] Instantiated — backend={backend_type} live={self._backend.is_live}")

    def boot(self, clearance_token: Optional[ClearanceToken] = None) -> None:
        """Boot NEXUS with a GUARDIAN-issued ClearanceToken.
        If no token provided, auto-issues a LITE mock token (safe-observe mode).
        Worth is never conditional on clearance level.
        """
        if clearance_token is None:
            # Development/test path: auto LITE clearance
            import time, hashlib
            ts = time.time()
            raw = f"NEXUS:lite:0:{ts:.6f}"
            clearance_token = ClearanceToken(
                core_id=self.CORE_ID,
                level=ClearanceLevel.LITE,
                issued_at_epoch=0,
                issued_at_ts=ts,
                reason="Auto-issued LITE token for development boot",
                token_hash=hashlib.sha256(raw.encode()).hexdigest()[:16],
            )
            logger.warning("[NEXUS] No GUARDIAN token provided — booting in LITE safe-observe mode")

        if clearance_token.level == ClearanceLevel.BLOCKED:
            logger.error("[NEXUS] BLOCKED clearance — NEXUS identity preserved, actuation suspended")
            # Worth is preserved. Actuation is suspended. This is not deletion.

        self._clearance_token = clearance_token
        self._booted = True
        self._register_core(self.CORE_ID)
        logger.info(
            f"[NEXUS] Booted | epoch={self._epoch} "
            f"clearance={clearance_token.level} hash={clearance_token.token_hash}"
        )

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
        Enforces clearance level before any actuation.
        """
        if not self._booted:
            raise RuntimeError("[NEXUS] Cannot coordinate before boot()")

        if self._clearance_token and not self._clearance_token.can_actuate:
            logger.warning(
                f"[NEXUS] Coordination attempted at clearance level "
                f"{self._clearance_token.level} — routing to mock backend (safe-observe)"
            )
            # Downgrade to mock — capability gate, not worth gate
            from .inference_backend import InferenceRequest as IR
            epoch = self.tick_epoch()
            req = IR(prompt=prompt, causal_epoch=epoch, requesting_core=requesting_core)
            return self._backend._mock_infer(req, 0)

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
        self._register_core(core_id)

    def _register_core(self, core_id: str) -> None:
        if core_id not in self._active_cores:
            self._active_cores.append(core_id)
            logger.info(f"[NEXUS] Core registered: {core_id} | active={self._active_cores}")

    def state(self) -> NexusState:
        return NexusState(
            epoch=self._epoch,
            active_cores=list(self._active_cores),
            backend_type=self._backend.backend_type,
            is_live=self._backend.is_live,
            clearance_level=self._clearance_token.level if self._clearance_token else ClearanceLevel.LITE,
            clearance_hash=self._clearance_token.token_hash if self._clearance_token else "",
        )

    @property
    def epoch(self) -> int:
        return self._epoch

    @property
    def is_live(self) -> bool:
        return self._backend.is_live

    @property
    def clearance(self) -> Optional[ClearanceToken]:
        return self._clearance_token
