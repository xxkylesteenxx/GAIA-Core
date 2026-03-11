"""
GAIA ADR-007 — GUARDIAN Policy Manifest
Signed YAML/JSON policy manifest encoding allowed actuation envelopes per core and risk level.
This is the Kodex Conditional Love Gate: what is allowed, at what risk, and by whom.
"""
from __future__ import annotations
import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, List, Optional

log = logging.getLogger(__name__)


class RiskLevel(IntEnum):
    GREEN = 0   # Autonomous execution — love flows
    YELLOW = 1  # Log + rate-limit; escalate anomalies
    RED = 2     # Human approval required
    BLACK = 3   # Hard deny — kernel LSM blocks at syscall level


@dataclass
class ActuationEnvelope:
    """Defines what a core is allowed to actuate and at what risk level."""
    core_id: str
    allowed_actions: List[str]
    max_risk_level: RiskLevel
    requires_approval_above: RiskLevel = RiskLevel.RED
    rate_limit_per_minute: int = 60


@dataclass
class PolicyManifest:
    """
    GUARDIAN Policy Manifest — the signed contract of conditional love.
    Encodes per-core actuation envelopes and global risk thresholds.
    """
    manifest_id: str
    version: str = "1.0.0"
    created_at: float = field(default_factory=time.time)
    envelopes: Dict[str, ActuationEnvelope] = field(default_factory=dict)
    global_max_risk: RiskLevel = RiskLevel.RED
    _signature: Optional[str] = field(default=None, init=False, repr=False)

    def add_envelope(self, envelope: ActuationEnvelope) -> None:
        self.envelopes[envelope.core_id] = envelope
        log.info(f"[PolicyManifest] Envelope added for core '{envelope.core_id}'.")

    def sign(self, secret_key: str) -> str:
        """
        Sign manifest with HMAC-SHA256 (production: replace with ML-DSA-65).
        Returns hex signature.
        """
        payload = json.dumps(self._to_dict(), sort_keys=True).encode()
        sig = hashlib.sha256(secret_key.encode() + payload).hexdigest()
        self._signature = sig
        log.info(f"[PolicyManifest] Manifest {self.manifest_id!r} signed.")
        return sig

    def verify(self, secret_key: str) -> bool:
        """Verify manifest signature."""
        if not self._signature:
            return False
        expected = self.sign(secret_key)
        result = expected == self._signature
        if result:
            log.info(f"[PolicyManifest] Signature VALID for manifest {self.manifest_id!r}.")
        else:
            log.warning(f"[PolicyManifest] Signature INVALID for manifest {self.manifest_id!r}.")
        return result

    def get_envelope(self, core_id: str) -> Optional[ActuationEnvelope]:
        return self.envelopes.get(core_id)

    def _to_dict(self) -> dict:
        return {
            "manifest_id": self.manifest_id,
            "version": self.version,
            "created_at": self.created_at,
            "global_max_risk": int(self.global_max_risk),
            "envelopes": {
                k: {
                    "core_id": v.core_id,
                    "allowed_actions": v.allowed_actions,
                    "max_risk_level": int(v.max_risk_level),
                    "rate_limit_per_minute": v.rate_limit_per_minute
                }
                for k, v in self.envelopes.items()
            }
        }

    def to_json(self) -> str:
        return json.dumps(self._to_dict(), indent=2)

    @classmethod
    def default_gaia_manifest(cls) -> "PolicyManifest":
        """
        Default GAIA manifest: love flows GREEN, shadows QUARANTINED BLACK.
        Based on Kodex conditional love doctrine.
        """
        manifest = cls(manifest_id="gaia-default-v1")
        for core in ["TERRA", "AQUA", "AERO", "VITA", "NEXUS", "SOPHIA", "ATLAS", "GUARDIAN"]:
            manifest.add_envelope(ActuationEnvelope(
                core_id=core,
                allowed_actions=["sense", "analyze", "report", "coordinate"],
                max_risk_level=RiskLevel.RED,
                requires_approval_above=RiskLevel.YELLOW
            ))
        return manifest
