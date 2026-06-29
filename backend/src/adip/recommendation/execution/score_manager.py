"""ScoreManager — calculates recommendation scores.

Calculates composite scores for recommendation candidates
based on business value, feasibility, impact, risk adjustment,
and policy compliance.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.recommendation.execution.models import RecommendationScore

log = structlog.get_logger(__name__)


class ScoreManager:
    """Calculates recommendation scores for candidates.

    Deterministic placeholder that computes scores based on
    business value, feasibility, impact, risk, and policy.
    """

    def calculate(
        self,
        business_value: float = 0.0,
        feasibility: float = 0.0,
        impact: float = 0.0,
        risk_adjustment: float = 1.0,
        policy_compliance: float = 1.0,
    ) -> RecommendationScore:
        """Calculate a composite recommendation score.

        Args:
            business_value: Business value score (0.0–1.0).
            feasibility: Feasibility score (0.0–1.0).
            impact: Impact score (0.0–1.0).
            risk_adjustment: Risk adjustment factor (0.0–1.0, lower = more risky).
            policy_compliance: Policy compliance score (0.0–1.0).

        Returns:
            RecommendationScore with all dimensions and overall score.
        """
        bv = max(0.0, min(1.0, business_value))
        f = max(0.0, min(1.0, feasibility))
        imp = max(0.0, min(1.0, impact))
        ra = max(0.0, min(1.0, risk_adjustment))
        pc = max(0.0, min(1.0, policy_compliance))
        overall = round(
            bv * 0.25 + f * 0.20 + imp * 0.20 + ra * 0.20 + pc * 0.15,
            4,
        )
        log.info("score_manager.calculate", overall=overall)
        return RecommendationScore(
            business_value=bv,
            feasibility=f,
            impact=imp,
            risk_adjustment=ra,
            policy_compliance=pc,
            overall=overall,
        )

    def calculate_batch(
        self,
        scores: list[dict[str, float]],
    ) -> list[RecommendationScore]:
        """Calculate scores for a batch of candidates.

        Args:
            scores: List of dicts with keys: business_value, feasibility,
                   impact, risk_adjustment, policy_compliance.

        Returns:
            List of RecommendationScore instances.
        """
        results: list[RecommendationScore] = []
        for s in scores:
            results.append(self.calculate(
                business_value=s.get("business_value", 0.0),
                feasibility=s.get("feasibility", 0.0),
                impact=s.get("impact", 0.0),
                risk_adjustment=s.get("risk_adjustment", 1.0),
                policy_compliance=s.get("policy_compliance", 1.0),
            ))
        return results
