"""StrategySelector — selects reasoning strategy based on context.

Selects the appropriate reasoning strategy based on the
reasoning domain, goal type, constraints, and available data.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.reasoning.enums import ReasoningDomain, ReasoningGoalType, ReasoningStrategyType

log = structlog.get_logger(__name__)


class StrategySelector:
    """Selects reasoning strategies based on context.

    Deterministic placeholder that chooses a reasoning strategy
    using simple rules based on domain, goal type, and constraints.
    """

    def select_strategy(
        self,
        domain: ReasoningDomain = ReasoningDomain.SYSTEM,
        goal_type: ReasoningGoalType | None = None,
        has_evidence: bool = True,
        has_rules: bool = True,
        complexity: str = "medium",
    ) -> ReasoningStrategyType:
        """Select the best reasoning strategy for the given context.

        Args:
            domain: The reasoning domain.
            goal_type: Optional goal type to guide selection.
            has_evidence: Whether evidence data is available.
            has_rules: Whether rules are available.
            complexity: Problem complexity (low, medium, high).

        Returns:
            The selected ReasoningStrategyType.
        """
        if goal_type == ReasoningGoalType.ROOT_CAUSE_ANALYSIS:
            return ReasoningStrategyType.HYPOTHESIS
        if goal_type == ReasoningGoalType.COMPLIANCE_VERIFICATION:
            return ReasoningStrategyType.RULE_BASED
        if goal_type == ReasoningGoalType.NEXT_BEST_ACTION:
            return ReasoningStrategyType.EVIDENCE_BASED
        if goal_type == ReasoningGoalType.MAINTENANCE_PLANNING:
            return ReasoningStrategyType.CONSTRAINT
        if goal_type == ReasoningGoalType.ENERGY_OPTIMIZATION:
            return ReasoningStrategyType.CONSTRAINT
        if goal_type == ReasoningGoalType.RISK_ASSESSMENT:
            return ReasoningStrategyType.MULTI_STEP
        if goal_type == ReasoningGoalType.ANOMALY_INVESTIGATION:
            return ReasoningStrategyType.EVIDENCE_BASED

        if complexity == "high":
            return ReasoningStrategyType.MULTI_STEP
        if has_evidence and has_rules:
            return ReasoningStrategyType.HYBRID
        if has_evidence:
            return ReasoningStrategyType.EVIDENCE_BASED
        if has_rules:
            return ReasoningStrategyType.RULE_BASED
        return ReasoningStrategyType.HYBRID

    def get_available_strategies(
        self,
        domain: ReasoningDomain = ReasoningDomain.SYSTEM,
    ) -> list[ReasoningStrategyType]:
        """Get all available strategies for a domain.

        Args:
            domain: The reasoning domain.

        Returns:
            List of all ReasoningStrategyType values.
        """
        return list(ReasoningStrategyType)

    def rank_strategies(
        self,
        domain: ReasoningDomain = ReasoningDomain.SYSTEM,
        goal_type: ReasoningGoalType | None = None,
    ) -> list[tuple[ReasoningStrategyType, float]]:
        """Rank strategies by suitability for the given context.

        Args:
            domain: The reasoning domain.
            goal_type: Optional goal type.

        Returns:
            List of (strategy, score) tuples sorted by score descending.
        """
        rankings: list[tuple[ReasoningStrategyType, float]] = [
            (ReasoningStrategyType.RULE_BASED, 0.6),
            (ReasoningStrategyType.EVIDENCE_BASED, 0.7),
            (ReasoningStrategyType.HYPOTHESIS, 0.5),
            (ReasoningStrategyType.CONSTRAINT, 0.4),
            (ReasoningStrategyType.MULTI_STEP, 0.3),
            (ReasoningStrategyType.HYBRID, 0.8),
        ]
        if goal_type == ReasoningGoalType.ROOT_CAUSE_ANALYSIS:
            rankings = [
                (ReasoningStrategyType.HYPOTHESIS, 0.9),
                (ReasoningStrategyType.EVIDENCE_BASED, 0.7),
                (ReasoningStrategyType.MULTI_STEP, 0.6),
                (ReasoningStrategyType.HYBRID, 0.5),
                (ReasoningStrategyType.RULE_BASED, 0.3),
                (ReasoningStrategyType.CONSTRAINT, 0.2),
            ]
        elif goal_type == ReasoningGoalType.COMPLIANCE_VERIFICATION:
            rankings = [
                (ReasoningStrategyType.RULE_BASED, 0.9),
                (ReasoningStrategyType.CONSTRAINT, 0.7),
                (ReasoningStrategyType.HYBRID, 0.5),
                (ReasoningStrategyType.EVIDENCE_BASED, 0.4),
                (ReasoningStrategyType.MULTI_STEP, 0.3),
                (ReasoningStrategyType.HYPOTHESIS, 0.2),
            ]

        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings
