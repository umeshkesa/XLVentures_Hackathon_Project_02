"""DecisionQualityManager — calculates decision quality metrics.

Assesses decision quality across evidence coverage, rule coverage,
goal satisfaction, constraint satisfaction, and assumption completeness.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.reasoning.execution.models import DecisionQuality

log = structlog.get_logger(__name__)


class DecisionQualityManager:
    """Calculates decision quality metrics.

    Deterministic placeholder that computes quality scores based on
    evidence coverage, rule coverage, goal satisfaction, constraint
    satisfaction, and assumption completeness.
    """

    def __init__(self) -> None:
        self._qualities: dict[str, DecisionQuality] = {}

    def calculate_evidence_coverage(
        self,
        evidence_covered: int = 0,
        total_evidence: int = 0,
    ) -> float:
        """Calculate proportion of evidence covered.

        Args:
            evidence_covered: Number of evidence items covered.
            total_evidence: Total number of evidence items.

        Returns:
            Evidence coverage score (0.0–1.0).
        """
        if total_evidence <= 0:
            return 0.0
        return round(min(1.0, evidence_covered / total_evidence), 4)

    def calculate_rule_coverage(
        self,
        rules_applied: int = 0,
        total_rules: int = 0,
    ) -> float:
        """Calculate proportion of rules applied.

        Args:
            rules_applied: Number of rules applied.
            total_rules: Total number of rules.

        Returns:
            Rule coverage score (0.0–1.0).
        """
        if total_rules <= 0:
            return 0.0
        return round(min(1.0, rules_applied / total_rules), 4)

    def calculate_goal_satisfaction(
        self,
        goals_achieved: int = 0,
        total_goals: int = 0,
    ) -> float:
        """Calculate proportion of goals achieved.

        Args:
            goals_achieved: Number of goals achieved.
            total_goals: Total number of goals.

        Returns:
            Goal satisfaction score (0.0–1.0).
        """
        if total_goals <= 0:
            return 0.0
        return round(min(1.0, goals_achieved / total_goals), 4)

    def calculate_constraint_satisfaction(
        self,
        satisfied_count: int = 0,
        total_constraints: int = 0,
    ) -> float:
        """Calculate proportion of constraints satisfied.

        Args:
            satisfied_count: Number of constraints satisfied.
            total_constraints: Total number of constraints.

        Returns:
            Constraint satisfaction score (0.0–1.0).
        """
        if total_constraints <= 0:
            return 0.0
        return round(min(1.0, satisfied_count / total_constraints), 4)

    def calculate_assumption_completeness(
        self,
        validated_count: int = 0,
        total_assumptions: int = 0,
    ) -> float:
        """Calculate proportion of assumptions validated.

        Args:
            validated_count: Number of assumptions validated.
            total_assumptions: Total number of assumptions.

        Returns:
            Assumption completeness score (0.0–1.0).
        """
        if total_assumptions <= 0:
            return 0.0
        return round(min(1.0, validated_count / total_assumptions), 4)

    def calculate_overall_quality(
        self,
        evidence_coverage: float = 0.0,
        rule_coverage: float = 0.0,
        goal_satisfaction: float = 0.0,
        constraint_satisfaction: float = 0.0,
        assumption_completeness: float = 0.0,
    ) -> DecisionQuality:
        """Calculate overall quality as weighted average of all dimensions.

        Args:
            evidence_coverage: Evidence coverage score (0.0–1.0).
            rule_coverage: Rule coverage score (0.0–1.0).
            goal_satisfaction: Goal satisfaction score (0.0–1.0).
            constraint_satisfaction: Constraint satisfaction score (0.0–1.0).
            assumption_completeness: Assumption completeness score (0.0–1.0).

        Returns:
            A DecisionQuality instance with all dimensions and overall score.
        """
        dimensions = [
            evidence_coverage,
            rule_coverage,
            goal_satisfaction,
            constraint_satisfaction,
            assumption_completeness,
        ]
        overall = round(sum(dimensions) / len(dimensions), 4)
        quality = DecisionQuality(
            evidence_coverage=evidence_coverage,
            rule_coverage=rule_coverage,
            goal_satisfaction=goal_satisfaction,
            constraint_satisfaction=constraint_satisfaction,
            assumption_completeness=assumption_completeness,
            overall=overall,
        )
        self._qualities[quality.quality_id] = quality
        log.info(
            "decision_quality.calculate_overall_quality",
            quality_id=quality.quality_id,
            overall=overall,
        )
        return quality

    def count(self) -> int:
        """Get the number of tracked quality assessments.

        Returns:
            Quality assessment count.
        """
        return len(self._qualities)

    def clear(self) -> None:
        """Clear all tracked quality assessments."""
        self._qualities.clear()
