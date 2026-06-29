"""Deterministic StrategySelector implementation."""

from __future__ import annotations

from adip.planner.contracts.models import PlanningContext, PlanningGoal
from adip.planner.enums import PlanningStrategyEnum
from adip.planner.interfaces.pipeline import StrategySelector


class DeterministicStrategySelector(StrategySelector):
    """Placeholder strategy selector based on goal priority.

    Maps priority to strategy:
      - CRITICAL → BEST_FIRST
      - HIGH     → GREEDY
      - MEDIUM   → DEFAULT
      - LOW      → PESSIMISTIC
    """

    _PRIORITY_STRATEGY_MAP: dict[str, PlanningStrategyEnum] = {
        "CRITICAL": PlanningStrategyEnum.BEST_FIRST,
        "HIGH": PlanningStrategyEnum.GREEDY,
        "MEDIUM": PlanningStrategyEnum.DEFAULT,
        "LOW": PlanningStrategyEnum.PESSIMISTIC,
    }

    async def select(
        self, goal: PlanningGoal, context: PlanningContext
    ) -> PlanningStrategyEnum:
        """Select a strategy based on the goal's priority."""
        return self._PRIORITY_STRATEGY_MAP.get(
            goal.priority.name,
            PlanningStrategyEnum.DEFAULT,
        )
