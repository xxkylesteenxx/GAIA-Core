"""
GAIA ADR-007 — GUARDIAN Legal Engine
Jurisdiction-aware rule evaluator for actuation requests.
Ensures GAIA operates within legal and ethical bounds globally.
"""
from __future__ import annotations
import logging
from dataclasses import dataclass
from enum import StrEnum
from typing import Dict, List, Optional, Set
from .policy_manifest import RiskLevel
from .risk_classifier import ActuationRequest, ClassificationResult

log = logging.getLogger(__name__)


class Jurisdiction(StrEnum):
    GLOBAL = "global"
    EU = "eu"           # GDPR, AI Act
    US = "us"           # CCPA, Executive Orders
    CN = "cn"           # PIPL, Cybersecurity Law
    RESTRICTED = "restricted"  # Embargoed/sanctioned


@dataclass
class JurisdictionRule:
    """A jurisdiction-specific rule that can elevate or deny an action."""
    jurisdiction: Jurisdiction
    restricted_actions: Set[str]
    elevated_to_red: Set[str]  # Actions elevated to RED in this jurisdiction
    reason_template: str


# GAIA built-in jurisdiction rules
DEFAULT_JURISDICTION_RULES: Dict[Jurisdiction, JurisdictionRule] = {
    Jurisdiction.EU: JurisdictionRule(
        jurisdiction=Jurisdiction.EU,
        restricted_actions={"export_personal_data", "cross_border_transfer"},
        elevated_to_red={"ingest_external_data", "federate_external_node"},
        reason_template="EU GDPR/AI Act restricts '{action}' in this jurisdiction."
    ),
    Jurisdiction.US: JurisdictionRule(
        jurisdiction=Jurisdiction.US,
        restricted_actions={"export_biometric_data"},
        elevated_to_red={"cross_core_write"},
        reason_template="US CCPA restricts '{action}' in this jurisdiction."
    ),
    Jurisdiction.RESTRICTED: JurisdictionRule(
        jurisdiction=Jurisdiction.RESTRICTED,
        restricted_actions={"*"},  # All actions denied
        elevated_to_red=set(),
        reason_template="Jurisdiction RESTRICTED: '{action}' hard denied."
    ),
}


class LegalEngine:
    """
    Evaluates actuation requests against jurisdiction rules.
    Integrates with RiskClassifier output to produce final legal clearance.
    """
    def __init__(self, active_jurisdictions: List[Jurisdiction] | None = None) -> None:
        self.active_jurisdictions = active_jurisdictions or [Jurisdiction.GLOBAL]
        self.rules = DEFAULT_JURISDICTION_RULES

    def evaluate(
        self,
        request: ActuationRequest,
        classification: ClassificationResult
    ) -> ClassificationResult:
        """
        Apply jurisdiction rules on top of risk classification.
        Returns updated ClassificationResult (may elevate risk level or deny).
        """
        for jur in self.active_jurisdictions:
            rule = self.rules.get(jur)
            if not rule:
                continue

            action = request.action.lower()

            # Hard deny: RESTRICTED jurisdiction or action in restricted set
            if "*" in rule.restricted_actions or action in rule.restricted_actions:
                log.warning(f"[LegalEngine] '{action}' DENIED by {jur.value} rules.")
                return ClassificationResult(
                    request_id=request.request_id,
                    core_id=request.core_id,
                    action=action,
                    risk_level=RiskLevel.BLACK,
                    reason=rule.reason_template.format(action=action),
                    allowed=False
                )

            # Elevation: bump to RED
            if action in rule.elevated_to_red and classification.risk_level < RiskLevel.RED:
                log.info(f"[LegalEngine] '{action}' elevated to RED by {jur.value} rules.")
                classification = ClassificationResult(
                    request_id=request.request_id,
                    core_id=request.core_id,
                    action=action,
                    risk_level=RiskLevel.RED,
                    reason=rule.reason_template.format(action=action),
                    allowed=True
                )

        return classification
