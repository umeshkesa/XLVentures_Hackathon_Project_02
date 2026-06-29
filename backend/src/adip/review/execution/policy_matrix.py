"""ReviewPolicyMatrix — deterministic policy matrix for review workflows.

Evaluates review requests against configurable thresholds to
determine the appropriate approval workflow, confidence level,
risk level, impact level, criticality level, and escalation needs.
"""

from __future__ import annotations

import structlog

from adip.review.execution.models import PolicyMatrixResult

log = structlog.get_logger(__name__)


class ReviewPolicyMatrix:
    """Deterministic policy matrix for routing review requests.

    Evaluates confidence, risk, impact, criticality, and compliance
    parameters against predefined thresholds to recommend an
    approval workflow strategy.
    """

    def __init__(self) -> None:
        self._matrix: dict[str, dict[str, str]] = {}

    def evaluate(
        self,
        confidence: float,
        risk: str,
        impact: str,
        criticality: str,
        compliance: bool,
    ) -> PolicyMatrixResult:
        """Evaluate parameters against the policy matrix.

        Deterministic routing logic:
        - confidence >= 0.9 AND risk == LOW AND impact == LOW AND criticality == LOW -> AUTO_APPROVAL
        - confidence >= 0.7 AND compliance -> SINGLE_REVIEW
        - confidence >= 0.5 AND (risk == HIGH or impact == HIGH) -> SEQUENTIAL
        - risk == HIGH AND impact == HIGH -> MULTI_LEVEL
        - criticality == EMERGENCY -> EMERGENCY
        - otherwise -> SINGLE_REVIEW
        """
        log.info(
            "review_policy_matrix.evaluate",
            confidence=confidence,
            risk=risk,
            impact=impact,
            criticality=criticality,
            compliance=compliance,
        )

        if confidence >= 0.9 and risk == "LOW" and impact == "LOW" and criticality == "LOW":
            workflow = "AUTO_APPROVAL"
            confidence_level = "HIGH"
            risk_level = "LOW"
            impact_level = "LOW"
            criticality_level = "LOW"
            requires_escalation = False
            justification = "High confidence with low risk, impact, and criticality"
        elif confidence >= 0.7 and compliance:
            workflow = "SINGLE_REVIEW"
            confidence_level = "HIGH"
            risk_level = risk
            impact_level = impact
            criticality_level = criticality
            requires_escalation = False
            justification = "High confidence with compliance satisfied; single review sufficient"
        elif confidence >= 0.5 and (risk == "HIGH" or impact == "HIGH"):
            workflow = "SEQUENTIAL"
            confidence_level = "MEDIUM"
            risk_level = risk
            impact_level = impact
            criticality_level = criticality
            requires_escalation = False
            justification = "Moderate confidence with elevated risk or impact; sequential review required"
        elif risk == "HIGH" and impact == "HIGH":
            workflow = "MULTI_LEVEL"
            confidence_level = "LOW"
            risk_level = "HIGH"
            impact_level = "HIGH"
            criticality_level = criticality
            requires_escalation = True
            justification = "High risk and high impact require multi-level approval"
        elif criticality == "EMERGENCY":
            workflow = "EMERGENCY"
            confidence_level = "LOW"
            risk_level = risk
            impact_level = impact
            criticality_level = "EMERGENCY"
            requires_escalation = True
            justification = "Emergency criticality triggers emergency approval protocol"
        else:
            workflow = "SINGLE_REVIEW"
            confidence_level = "MEDIUM"
            risk_level = risk
            impact_level = impact
            criticality_level = criticality
            requires_escalation = False
            justification = "Default routing to single review"

        result = PolicyMatrixResult(
            recommended_workflow=workflow,
            confidence_level=confidence_level,
            risk_level=risk_level,
            impact_level=impact_level,
            criticality_level=criticality_level,
            compliance_required=compliance,
            requires_escalation=requires_escalation,
            justification=justification,
        )

        log.info(
            "review_policy_matrix.evaluated",
            workflow=workflow,
            confidence_level=confidence_level,
            justification=justification,
        )
        return result

    def get_matrix(
        self,
        confidence: float,
        risk: str,
        impact: str,
        criticality: str,
        compliance: bool,
    ) -> dict[str, str]:
        """Return the raw matrix mapping for the given parameters."""
        log.info(
            "review_policy_matrix.get_matrix",
            confidence=confidence,
            risk=risk,
            impact=impact,
            criticality=criticality,
            compliance=compliance,
        )
        result = self.evaluate(confidence, risk, impact, criticality, compliance)
        matrix = {
            "recommended_workflow": result.recommended_workflow,
            "confidence_level": result.confidence_level,
            "risk_level": result.risk_level,
            "impact_level": result.impact_level,
            "criticality_level": result.criticality_level,
            "compliance_required": str(result.compliance_required),
            "requires_escalation": str(result.requires_escalation),
            "justification": result.justification,
        }
        return matrix

    def clear(self) -> None:
        """Clear the internal matrix state."""
        log.info("review_policy_matrix.clear")
        self._matrix.clear()
