"""RecommendationConfidenceCalculator — calculates recommendation confidence.

Computes multi-dimensional confidence scores for recommendation
results based on reasoning confidence, business score, feasibility,
policy compliance, outcome prediction, and portfolio quality.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.recommendation.contracts.models import RecommendationConfidence

log = structlog.get_logger(__name__)


class RecommendationConfidenceCalculator:
    """Calculates recommendation confidence scores.

    Deterministic placeholder that computes a 6-dimension confidence
    assessment based on reasoning confidence, business score,
    feasibility, policy compliance, outcome prediction, and
    portfolio quality.
    """

    def calculate(
        self,
        reasoning_confidence: float = 0.0,
        business_score: float = 0.0,
        feasibility: float = 0.0,
        policy_compliance: float = 1.0,
        outcome_prediction: float = 0.0,
        portfolio_quality: float = 0.0,
    ) -> RecommendationConfidence:
        """Calculate a multi-dimensional confidence score.

        Args:
            reasoning_confidence: Confidence from reasoning engine (0.0-1.0).
            business_score: Business value score (0.0-1.0).
            feasibility: Feasibility score (0.0-1.0).
            policy_compliance: Policy compliance score (0.0-1.0).
            outcome_prediction: Outcome prediction confidence (0.0-1.0).
            portfolio_quality: Portfolio quality score (0.0-1.0).

        Returns:
            RecommendationConfidence with all dimensions.
        """
        rc = max(0.0, min(1.0, reasoning_confidence))
        bs = max(0.0, min(1.0, business_score))
        f = max(0.0, min(1.0, feasibility))
        pc = max(0.0, min(1.0, policy_compliance))
        op = max(0.0, min(1.0, outcome_prediction))
        pq = max(0.0, min(1.0, portfolio_quality))

        strategy_confidence = round((rc + bs) / 2, 4)
        impact_accuracy = round((bs + f) / 2, 4)
        benefit_reliability = round((rc + op) / 2, 4)
        risk_assessment = round((pc + f) / 2, 4)
        constraint_compliance = pc

        overall = round(
            strategy_confidence * 0.20
            + impact_accuracy * 0.20
            + benefit_reliability * 0.15
            + risk_assessment * 0.15
            + constraint_compliance * 0.15
            + pq * 0.15,
            4,
        )

        log.info("confidence.calculate", overall=overall)
        return RecommendationConfidence(
            overall_confidence=overall,
            strategy_confidence=strategy_confidence,
            impact_accuracy=impact_accuracy,
            benefit_reliability=benefit_reliability,
            risk_assessment=risk_assessment,
            constraint_compliance=constraint_compliance,
        )
