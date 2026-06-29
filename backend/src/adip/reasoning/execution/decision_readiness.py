"""DecisionReadiness — assesses whether a decision is ready to be made.

Evaluates readiness based on confidence, risk, uncertainty,
contradictions, constraint violations, alternatives, and quality.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog

from adip.reasoning.execution.models import DecisionReadinessResult

log = structlog.get_logger(__name__)


class DecisionReadiness:
    """Assesses whether a decision is ready to be made.

    Deterministic placeholder that evaluates readiness across
    confidence, risk, uncertainty, contradictions, constraints,
    alternatives, and quality dimensions.
    """

    READY = "READY"
    NOT_READY = "NOT_READY"
    MORE_INFORMATION_REQUIRED = "MORE_INFORMATION_REQUIRED"

    def __init__(self) -> None:
        self._results: dict[str, DecisionReadinessResult] = {}

    def assess_readiness(
        self,
        confidence: float = 0.0,
        risk_score: float = 0.0,
        uncertainty_count: int = 0,
        contradiction_count: int = 0,
        constraint_violations: int = 0,
        alternatives_count: int = 0,
        quality_score: float = 0.0,
    ) -> DecisionReadinessResult:
        """Assess readiness for a decision.

        Evaluates all input dimensions to determine whether the
        decision is READY, NOT_READY, or needs MORE_INFORMATION_REQUIRED.

        Args:
            confidence: Overall confidence score (0.0–1.0).
            risk_score: Overall risk score (0.0–1.0).
            uncertainty_count: Number of unresolved uncertainties.
            contradiction_count: Number of unresolved contradictions.
            constraint_violations: Number of constraint violations.
            alternatives_count: Number of alternatives available.
            quality_score: Overall quality score (0.0–1.0).

        Returns:
            A DecisionReadinessResult with the assessment.
        """
        factors: dict[str, Any] = {
            "confidence": confidence,
            "risk_score": risk_score,
            "uncertainty_count": uncertainty_count,
            "contradiction_count": contradiction_count,
            "constraint_violations": constraint_violations,
            "alternatives_count": alternatives_count,
            "quality_score": quality_score,
        }
        recommendations: list[str] = []

        is_ready = (
            confidence >= 0.7
            and risk_score < 0.5
            and uncertainty_count == 0
            and contradiction_count == 0
            and constraint_violations == 0
            and alternatives_count > 0
            and quality_score >= 0.7
        )

        is_not_ready = (
            confidence < 0.3
            or risk_score >= 0.8
            or quality_score < 0.3
        )

        if is_ready:
            readiness = self.READY
            overall_score = round(
                (confidence * 0.3
                 + (1.0 - risk_score) * 0.3
                 + quality_score * 0.4),
                4,
            )
        elif is_not_ready:
            readiness = self.NOT_READY
            overall_score = round(
                (confidence * 0.3
                 + (1.0 - risk_score) * 0.3
                 + quality_score * 0.4),
                4,
            )
            if confidence < 0.3:
                recommendations.append("Improve confidence to at least 0.3")
            if risk_score >= 0.8:
                recommendations.append("Reduce risk score below 0.8")
            if quality_score < 0.3:
                recommendations.append("Improve quality score to at least 0.3")
        else:
            readiness = self.MORE_INFORMATION_REQUIRED
            overall_score = round(
                (confidence * 0.3
                 + (1.0 - risk_score) * 0.3
                 + quality_score * 0.4),
                4,
            )
            if confidence < 0.7:
                recommendations.append("Increase confidence to at least 0.7")
            if risk_score >= 0.5:
                recommendations.append("Reduce risk score below 0.5")
            if uncertainty_count > 0:
                recommendations.append(f"Resolve {uncertainty_count} uncertainty(ies)")
            if contradiction_count > 0:
                recommendations.append(f"Resolve {contradiction_count} contradiction(s)")
            if constraint_violations > 0:
                recommendations.append(f"Address {constraint_violations} constraint violation(s)")
            if alternatives_count == 0:
                recommendations.append("Generate at least one alternative")
            if quality_score < 0.7:
                recommendations.append("Improve quality score to at least 0.7")

        decision_id = str(uuid.uuid4())
        result = DecisionReadinessResult(
            decision_id=decision_id,
            readiness=readiness,
            overall_score=overall_score,
            confidence_score=confidence,
            risk_score=risk_score,
            quality_score=quality_score,
            factors=factors,
            recommendations=recommendations,
        )
        self._results[decision_id] = result
        log.info(
            "decision_readiness.assess",
            decision_id=decision_id,
            readiness=readiness,
            overall_score=overall_score,
        )
        return result

    def get_readiness(
        self,
        decision_id: str,
    ) -> DecisionReadinessResult | None:
        """Get a readiness assessment by decision ID.

        Args:
            decision_id: The decision identifier.

        Returns:
            The DecisionReadinessResult if found, else None.
        """
        return self._results.get(decision_id)

    def get_all_readiness(self) -> list[DecisionReadinessResult]:
        """Get all readiness assessments.

        Returns:
            List of all DecisionReadinessResult instances.
        """
        return list(self._results.values())

    def clear(self) -> None:
        """Clear all readiness assessments."""
        self._results.clear()

    def count(self) -> int:
        """Get the number of readiness assessments.

        Returns:
            Readiness assessment count.
        """
        return len(self._results)
