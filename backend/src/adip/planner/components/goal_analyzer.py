"""Deterministic GoalAnalyzer implementation."""

from __future__ import annotations

from adip.planner.contracts.models import PlanningGoal
from adip.planner.interfaces.pipeline import GoalAnalyzer


class DeterministicGoalAnalyzer(GoalAnalyzer):
    """Placeholder goal analyzer.

    Enriches the goal by populating intent, domain, entities, and
    ambiguity_score via keyword heuristics.
    """

    _DOMAIN_KEYWORDS: dict[str, str] = {
        "search": "search",
        "find": "search",
        "lookup": "search",
        "compute": "computation",
        "calculate": "computation",
        "analyze": "analytics",
        "report": "analytics",
        "summarise": "summarization",
        "summarize": "summarization",
        "translate": "translation",
    }

    _INTENT_KEYWORDS: dict[str, str] = {
        "find": "information_retrieval",
        "search": "information_retrieval",
        "lookup": "information_retrieval",
        "compute": "computation",
        "calculate": "computation",
        "create": "content_generation",
        "generate": "content_generation",
        "analyze": "analysis",
        "analyse": "analysis",
        "compare": "analysis",
        "summarise": "summarization",
        "summarize": "summarization",
        "translate": "translation",
    }

    async def analyze(self, goal: PlanningGoal) -> PlanningGoal:
        """Analyze and enrich the goal."""
        if goal.domain is None:
            for keyword, domain in self._DOMAIN_KEYWORDS.items():
                if keyword in goal.objective.lower():
                    goal.domain = domain
                    break

        if goal.intent is None:
            for keyword, intent in self._INTENT_KEYWORDS.items():
                if keyword in goal.objective.lower():
                    goal.intent = intent
                    break

        # Simple ambiguity heuristic: short ≠ unambiguous
        word_count = len(goal.objective.split())
        goal.ambiguity_score = round(max(0.0, 1.0 - word_count / 20.0), 4)

        if not goal.entities:
            goal.entities = []

        if not goal.success_criteria:
            goal.success_criteria = ["task_completion"]

        return goal
