"""StrategySelector — selects recommendation strategy based on context.

Selects the appropriate recommendation strategy based on
goals, domain, policy, and context.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.recommendation.enums import (
    RecommendationDomain,
    RecommendationGoal,
    RecommendationStrategy,
)

log = structlog.get_logger(__name__)


class StrategySelector:
    """Selects recommendation strategies based on context.

    Deterministic placeholder that chooses a recommendation strategy
    using simple rules based on goals, domain, and context.
    """

    def select_strategy(
        self,
        goals: list[RecommendationGoal] | None = None,
        domain: RecommendationDomain = RecommendationDomain.GENERAL,
        has_policy: bool = True,
        has_context: bool = True,
    ) -> RecommendationStrategy:
        """Select the best recommendation strategy for the given context.

        Args:
            goals: Optional list of recommendation goals.
            domain: The recommendation domain.
            has_policy: Whether policy data is available.
            has_context: Whether context data is available.

        Returns:
            The selected RecommendationStrategy.
        """
        goals = goals or []

        if RecommendationGoal.REDUCE_DOWNTIME in goals:
            return RecommendationStrategy.PREVENTIVE_MAINTENANCE
        if RecommendationGoal.REDUCE_COST in goals:
            return RecommendationStrategy.COST_OPTIMIZATION
        if RecommendationGoal.INCREASE_SAFETY in goals:
            return RecommendationStrategy.RISK_MITIGATION
        if RecommendationGoal.REDUCE_ENERGY_CONSUMPTION in goals:
            return RecommendationStrategy.ENERGY_OPTIMIZATION
        if RecommendationGoal.MEET_SLA in goals:
            return RecommendationStrategy.SLA_RECOVERY

        if domain == RecommendationDomain.ENERGY:
            return RecommendationStrategy.ENERGY_OPTIMIZATION
        if domain == RecommendationDomain.SAFETY:
            return RecommendationStrategy.RISK_MITIGATION
        if domain == RecommendationDomain.MAINTENANCE:
            return RecommendationStrategy.PREVENTIVE_MAINTENANCE

        if has_policy and has_context:
            return RecommendationStrategy.HYBRID_RECOMMENDATION
        return RecommendationStrategy.NEXT_BEST_ACTION

    def get_available_strategies(
        self,
        domain: RecommendationDomain = RecommendationDomain.GENERAL,
    ) -> list[RecommendationStrategy]:
        """Get all available strategies for a domain.

        Args:
            domain: The recommendation domain.

        Returns:
            List of all RecommendationStrategy values.
        """
        return list(RecommendationStrategy)

    def rank_strategies(
        self,
        goals: list[RecommendationGoal] | None = None,
        domain: RecommendationDomain = RecommendationDomain.GENERAL,
    ) -> list[tuple[RecommendationStrategy, float]]:
        """Rank strategies by suitability for the given context.

        Args:
            goals: Optional list of recommendation goals.
            domain: The recommendation domain.

        Returns:
            List of (strategy, score) tuples sorted by score descending.
        """
        rankings: list[tuple[RecommendationStrategy, float]] = [
            (RecommendationStrategy.NEXT_BEST_ACTION, 0.7),
            (RecommendationStrategy.RISK_MITIGATION, 0.6),
            (RecommendationStrategy.PREVENTIVE_MAINTENANCE, 0.5),
            (RecommendationStrategy.COST_OPTIMIZATION, 0.6),
            (RecommendationStrategy.ENERGY_OPTIMIZATION, 0.5),
            (RecommendationStrategy.SLA_RECOVERY, 0.4),
            (RecommendationStrategy.HYBRID_RECOMMENDATION, 0.8),
        ]
        goals = goals or []
        if RecommendationGoal.REDUCE_DOWNTIME in goals:
            rankings = [
                (RecommendationStrategy.PREVENTIVE_MAINTENANCE, 0.9),
                (RecommendationStrategy.HYBRID_RECOMMENDATION, 0.8),
                (RecommendationStrategy.NEXT_BEST_ACTION, 0.6),
                (RecommendationStrategy.RISK_MITIGATION, 0.5),
                (RecommendationStrategy.COST_OPTIMIZATION, 0.5),
                (RecommendationStrategy.ENERGY_OPTIMIZATION, 0.4),
                (RecommendationStrategy.SLA_RECOVERY, 0.3),
            ]
        elif RecommendationGoal.REDUCE_COST in goals:
            rankings = [
                (RecommendationStrategy.COST_OPTIMIZATION, 0.9),
                (RecommendationStrategy.NEXT_BEST_ACTION, 0.7),
                (RecommendationStrategy.HYBRID_RECOMMENDATION, 0.7),
                (RecommendationStrategy.RISK_MITIGATION, 0.5),
                (RecommendationStrategy.PREVENTIVE_MAINTENANCE, 0.5),
                (RecommendationStrategy.ENERGY_OPTIMIZATION, 0.4),
                (RecommendationStrategy.SLA_RECOVERY, 0.3),
            ]
        elif RecommendationGoal.INCREASE_SAFETY in goals:
            rankings = [
                (RecommendationStrategy.RISK_MITIGATION, 0.9),
                (RecommendationStrategy.HYBRID_RECOMMENDATION, 0.7),
                (RecommendationStrategy.NEXT_BEST_ACTION, 0.6),
                (RecommendationStrategy.PREVENTIVE_MAINTENANCE, 0.6),
                (RecommendationStrategy.COST_OPTIMIZATION, 0.4),
                (RecommendationStrategy.ENERGY_OPTIMIZATION, 0.3),
                (RecommendationStrategy.SLA_RECOVERY, 0.3),
            ]
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings
