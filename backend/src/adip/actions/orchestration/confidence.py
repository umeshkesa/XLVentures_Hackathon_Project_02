"""ActionConfidenceCalculator — multi-dimensional confidence for action plans.

Deterministic placeholder implementing 6-dimension weighted
confidence scoring: resource, schedule, cost, risk, feasibility,
and plan quality. Follows the ReviewConfidenceCalculator pattern.
"""

from __future__ import annotations

import structlog

from adip.actions.contracts.models import ActionConfidence

log = structlog.get_logger(__name__)


class ActionConfidenceCalculator:
    """Calculates multi-dimensional confidence for action plans.

    Combines 6 weighted dimensions into an overall confidence
    score between 0.0 and 1.0.
    """

    RESOURCE_WEIGHT = 0.20
    SCHEDULE_WEIGHT = 0.20
    COST_WEIGHT = 0.15
    RISK_WEIGHT = 0.20
    FEASIBILITY_WEIGHT = 0.15
    QUALITY_WEIGHT = 0.10

    def __init__(self) -> None:
        self._history: list[ActionConfidence] = []

    def calculate(
        self,
        resource_confidence: float = 0.0,
        schedule_confidence: float = 0.0,
        cost_confidence: float = 0.0,
        risk_confidence: float = 0.0,
        feasibility_confidence: float = 0.0,
        quality_score: float = 0.0,
    ) -> ActionConfidence:
        """Calculate overall confidence from individual dimensions.

        All inputs are clamped to [0.0, 1.0]. The overall score
        is a weighted average of all 6 dimensions.

        Args:
            resource_confidence: Resource availability confidence.
            schedule_confidence: Schedule feasibility confidence.
            cost_confidence: Cost estimate confidence.
            risk_confidence: Risk assessment confidence.
            feasibility_confidence: Plan feasibility confidence.
            quality_score: Plan quality score.

        Returns:
            ActionConfidence with all dimension scores.
        """
        rc = max(0.0, min(1.0, resource_confidence))
        sc = max(0.0, min(1.0, schedule_confidence))
        cc = max(0.0, min(1.0, cost_confidence))
        rk = max(0.0, min(1.0, risk_confidence))
        fc = max(0.0, min(1.0, feasibility_confidence))
        qs = max(0.0, min(1.0, quality_score))

        overall = (
            rc * self.RESOURCE_WEIGHT
            + sc * self.SCHEDULE_WEIGHT
            + cc * self.COST_WEIGHT
            + rk * self.RISK_WEIGHT
            + fc * self.FEASIBILITY_WEIGHT
            + qs * self.QUALITY_WEIGHT
        )

        confidence = ActionConfidence(
            overall_confidence=round(overall, 4),
            resource_confidence=rc,
            schedule_confidence=sc,
            cost_confidence=cc,
            risk_confidence=rk,
            feasibility_confidence=fc,
        )
        self._history.append(confidence)
        log.info(
            "confidence.calculated",
            overall=confidence.overall_confidence,
        )
        return confidence

    def get_history(self) -> list[ActionConfidence]:
        """Get all confidence calculations.

        Returns:
            List of ActionConfidence records.
        """
        return list(self._history)

    def clear(self) -> None:
        """Clear confidence history."""
        self._history.clear()
