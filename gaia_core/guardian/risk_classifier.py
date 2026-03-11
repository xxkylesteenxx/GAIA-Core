"""
GAIA ADR-007 — GUARDIAN Risk Classifier
Classifies actuation requests into Green/Yellow/Red/Black risk levels.
This is the conditional love gate: what gets through, what gets held, what gets blocked.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from .policy_manifest import RiskLevel, PolicyManifest

log = logging.getLogger(__name__)

# Actions always hard-denied (BLACK) regardless of manifest
BLACKLIST_ACTIONS = {
    "delete_identity_root",
    "disable_guardian",
    "bypass_approval_gate",
    "erase_actuation_log",
    "modify_pcr_policy",
}

# Actions requiring human approval (RED) by default
RED_ACTIONS = {
    "shutdown_core",
    "modify_policy_manifest",
    "federate_external_node",
    "export_identity_root",
    "override_rate_limit",
}

# Actions that log + rate-limit (YELLOW)
YELLOW_ACTIONS = {
    "ingest_external_data",
    "cross_core_write",
    "emit_actuation_signal",
    "update_world_model",
}


@dataclass
class ActuationRequest:
    """A request to actuate an action from a GAIA core."""
    request_id: str
    core_id: str
    action: str
    parameters: Dict = None
    context: Dict = None

    def __post_init__(self):
        self.parameters = self.parameters or {}
        self.context = self.context or {}


@dataclass
class ClassificationResult:
    request_id: str
    core_id: str
    action: str
    risk_level: RiskLevel
    reason: str
    allowed: bool


class RiskClassifier:
    """
    Classifies actuation requests by risk level.
    Applies blacklist, manifest envelope, and default rules.
    """
    def __init__(self, manifest: PolicyManifest) -> None:
        self.manifest = manifest

    def classify(self, request: ActuationRequest) -> ClassificationResult:
        action = request.action.lower()

        # BLACK: hard deny always
        if action in BLACKLIST_ACTIONS:
            return ClassificationResult(
                request_id=request.request_id,
                core_id=request.core_id,
                action=action,
                risk_level=RiskLevel.BLACK,
                reason=f"Action '{action}' is permanently blacklisted.",
                allowed=False
            )

        # Check manifest envelope for this core
        envelope = self.manifest.get_envelope(request.core_id)
        if envelope and action not in [a.lower() for a in envelope.allowed_actions]:
            # Action not in allowed list — elevate to RED
            if action in RED_ACTIONS:
                level = RiskLevel.RED
            elif action in YELLOW_ACTIONS:
                level = RiskLevel.YELLOW
            else:
                level = RiskLevel.RED  # Unknown = cautious
            log.warning(f"[RiskClassifier] Action '{action}' not in envelope for core '{request.core_id}'.")
            return ClassificationResult(
                request_id=request.request_id, core_id=request.core_id,
                action=action, risk_level=level,
                reason=f"Action not in manifest envelope for '{request.core_id}'.",
                allowed=(level < RiskLevel.BLACK)
            )

        # Apply default classification
        if action in RED_ACTIONS:
            level = RiskLevel.RED
        elif action in YELLOW_ACTIONS:
            level = RiskLevel.YELLOW
        else:
            level = RiskLevel.GREEN

        log.info(f"[RiskClassifier] '{action}' from '{request.core_id}' → {level.name}")
        return ClassificationResult(
            request_id=request.request_id, core_id=request.core_id,
            action=action, risk_level=level,
            reason=f"Default classification: {level.name}.",
            allowed=True
        )
