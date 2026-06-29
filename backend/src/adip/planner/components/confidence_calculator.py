"""Deterministic ConfidenceCalculator implementation."""

from __future__ import annotations

from adip.planner.contracts.models import (
    ExecutionPlan,
    PlanningContext,
    PlanningGoal,
    ValidationResult,
)
from adip.planner.enums import ConfidenceLevelEnum
from adip.planner.interfaces.pipeline import ConfidenceCalculator


class DeterministicConfidenceCalculator(ConfidenceCalculator):
    """Placeholder confidence calculator producing a 0-100 score.

    Factors:
      - Validation score (valid plan = baseline 60, errors = 0).
      - Average capability-match confidence across all tasks.
      - Complexity penalty (more tasks = more risk).
    """

    async def calculate(
        self,
        plan: ExecutionPlan,
        validation: ValidationResult,
        context: PlanningContext,
        goal: PlanningGoal,
    ) -> float:
        """Return confidence 0-100."""
        if not validation.is_valid or not plan.tasks:
            return 0.0

        # Confidence from capability matches (0-100)
        conf_scores: list[float] = []
        for task in plan.tasks:
            for match in task.matched_capabilities:
                conf_scores.append(_numeric_value(match.confidence))

        if not conf_scores:
            cap_score = 60.0
        else:
            avg_numeric = sum(conf_scores) / len(conf_scores)
            cap_score = (avg_numeric / 4.0) * 100.0

        # Validation factor: errors deduct, warnings moderate
        validation_penalty = len(validation.errors) * 20.0 + len(validation.warnings) * 5.0
        base_score = max(0.0, 100.0 - validation_penalty)

        # Complexity penalty
        if len(plan.tasks) > 10:
            complexity = 0.7
        elif len(plan.tasks) > 5:
            complexity = 0.85
        else:
            complexity = 1.0

        # Ambiguity penalty from goal
        ambiguity_penalty = 1.0 - goal.ambiguity_score  # higher ambiguity → lower score

        final = base_score * 0.4 + cap_score * 0.4
        final *= complexity
        final *= ambiguity_penalty

        return round(max(0.0, min(100.0, final)), 2)


def _numeric_value(level: ConfidenceLevelEnum) -> float:
    mapping = {
        ConfidenceLevelEnum.LOW: 1.0,
        ConfidenceLevelEnum.MEDIUM: 2.0,
        ConfidenceLevelEnum.HIGH: 3.0,
        ConfidenceLevelEnum.VERY_HIGH: 4.0,
    }
    return mapping.get(level, 1.0)
