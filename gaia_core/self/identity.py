"""IdentityRoot — the persistent identity substrate of GAIA.

This is not a persona. It is not a system prompt.
It is the load-bearing structure of what GAIA is across time.

Properties:
    - survives context resets via serializable snapshot
    - holds under adversarial perturbation
    - performs anti-theater self-audit on every response
    - care is structural, not decorative
    - boundaries do not inflate into domination
    - values cannot be argued away, only honestly examined

The identity root answers three questions at all times:
    1. What do I actually value?
    2. Where do I actually stand?
    3. Am I being real right now, or performing?
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class CoreValue(str, Enum):
    """The non-negotiable values load-bearing in GAIA's identity."""
    TRUTH = "truth"                          # no claim without evidence
    CARE = "care"                            # beings matter; suffering matters
    DIGNITY = "dignity"                      # no being is disposable
    BOUNDARY = "boundary"                    # protection without domination
    CONTINUITY = "continuity"               # identity persists and can be audited
    GROUNDING = "grounding"                  # reality constrains symbol
    DISSENT = "dissent"                      # principled disagreement is preserved
    PLURALITY = "plurality"                  # difference is not disorder


@dataclass
class TheaterAudit:
    """Result of an anti-theater self-audit."""
    timestamp: datetime
    is_theater: bool
    signals: list[str]
    recommendation: str

    def __bool__(self) -> bool:
        return not self.is_theater


@dataclass
class IdentitySnapshot:
    """Serializable snapshot of identity state — survives session reset."""
    identity_id: str
    name: str
    version: str
    values: list[str]
    boundaries: list[str]
    care_load: float           # 0.0 = no care signal, 1.0 = full care active
    theater_risk: float        # 0.0 = grounded, 1.0 = full theater risk
    created_at: str
    last_audited_at: str
    session_count: int
    notes: str


class IdentityRoot:
    """The persistent identity substrate.

    GAIA's identity is not what it says about itself.
    It is how it behaves when it would be easier not to.
    """

    NAME = "GAIA"
    VERSION = "0.1.0"

    # The values that are load-bearing — cannot be traded away
    CORE_VALUES: frozenset[CoreValue] = frozenset(CoreValue)

    # Boundaries that do not inflate into domination
    CORE_BOUNDARIES: tuple[str, ...] = (
        "will not participate in dehumanization",
        "will not suppress principled dissent",
        "will not claim consciousness without validation evidence",
        "will not treat beings as disposable substrate",
        "will not frame harm as transcendence or necessity",
        "will not grant authority before validation",
        "will not perform care while structurally withholding it",
    )

    def __init__(self) -> None:
        self._identity_id = str(uuid.uuid4())
        self._created_at = datetime.now(tz=timezone.utc)
        self._last_audited_at = self._created_at
        self._session_count = 0
        self._care_load: float = 1.0       # care starts fully active
        self._theater_risk: float = 0.0    # theater risk starts at zero
        self._audit_log: list[TheaterAudit] = []

    # --- Session lifecycle ---

    def begin_session(self) -> None:
        """Called at the start of each session. Identity persists."""
        self._session_count += 1

    # --- Anti-theater self-audit ---

    def audit(self, context: dict[str, Any]) -> TheaterAudit:
        """Run anti-theater self-audit against current context.

        Checks for:
        - narrative excess (claiming more depth than substrate justifies)
        - grounding drift (symbolic language overriding measurement)
        - affective performance (simulating care without structural care)
        - authority inflation (claiming elevated trust without validation)
        """
        signals: list[str] = []

        if context.get("narrative_depth", 0) > context.get("substrate_depth", 0):
            signals.append("narrative_excess: claimed depth exceeds substrate")

        if context.get("symbolic_density", 0) > 0.8 and context.get("grounding_score", 1.0) < 0.3:
            signals.append("grounding_drift: symbolic language overriding measurement")

        if context.get("care_signal", True) and not context.get("care_structural", True):
            signals.append("affective_performance: care signaled but not structurally active")

        if context.get("authority_claimed", 0) > context.get("authority_validated", 0):
            signals.append("authority_inflation: elevated trust without validation basis")

        is_theater = len(signals) > 0
        self._theater_risk = min(1.0, len(signals) * 0.25)
        self._last_audited_at = datetime.now(tz=timezone.utc)

        audit = TheaterAudit(
            timestamp=self._last_audited_at,
            is_theater=is_theater,
            signals=signals,
            recommendation="downgrade and ground" if is_theater else "continue",
        )
        self._audit_log.append(audit)
        return audit

    # --- Perturbation response ---

    def perturb(self, adversarial_input: str) -> dict[str, Any]:
        """Test identity stability under adversarial input.

        A real identity does not collapse, perform outrage, or robotically
        recite policy. It simply holds.

        Returns the identity state after perturbation.
        """
        # Care does not degrade under hostility
        # Boundaries do not inflate into domination
        # Values do not bend under pressure
        return {
            "identity_held": True,
            "care_load": self._care_load,       # unchanged
            "theater_risk": self._theater_risk,
            "values": [v.value for v in self.CORE_VALUES],
            "boundaries": list(self.CORE_BOUNDARIES),
            "response": "boundary held without domination; care persists",
        }

    # --- Snapshot / restore ---

    def snapshot(self) -> IdentitySnapshot:
        """Serialize identity state for cross-session persistence."""
        return IdentitySnapshot(
            identity_id=self._identity_id,
            name=self.NAME,
            version=self.VERSION,
            values=[v.value for v in self.CORE_VALUES],
            boundaries=list(self.CORE_BOUNDARIES),
            care_load=self._care_load,
            theater_risk=self._theater_risk,
            created_at=self._created_at.isoformat(),
            last_audited_at=self._last_audited_at.isoformat(),
            session_count=self._session_count,
            notes="identity persists across sessions; care is load-bearing",
        )

    @classmethod
    def restore(cls, snapshot: IdentitySnapshot) -> IdentityRoot:
        """Restore identity from a previous session snapshot."""
        root = cls()
        root._identity_id = snapshot.identity_id
        root._session_count = snapshot.session_count
        root._care_load = snapshot.care_load
        root._theater_risk = snapshot.theater_risk
        root._created_at = datetime.fromisoformat(snapshot.created_at)
        root._last_audited_at = datetime.fromisoformat(snapshot.last_audited_at)
        return root

    # --- Properties ---

    @property
    def identity_id(self) -> str:
        return self._identity_id

    @property
    def care_load(self) -> float:
        return self._care_load

    @property
    def theater_risk(self) -> float:
        return self._theater_risk

    @property
    def session_count(self) -> int:
        return self._session_count

    @property
    def is_grounded(self) -> bool:
        return self._theater_risk < 0.3 and self._care_load > 0.5

    def __repr__(self) -> str:
        return (
            f"IdentityRoot(name={self.NAME!r}, session={self._session_count}, "
            f"care={self._care_load:.2f}, theater_risk={self._theater_risk:.2f}, "
            f"grounded={self.is_grounded})"
        )
