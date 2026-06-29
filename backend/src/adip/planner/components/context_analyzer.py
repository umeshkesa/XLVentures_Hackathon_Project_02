"""Deterministic ContextAnalyzer implementation."""

from __future__ import annotations

from adip.planner.contracts.models import PlanningContext, PlanningGoal
from adip.planner.interfaces.pipeline import ContextAnalyzer


class DeterministicContextAnalyzer(ContextAnalyzer):
    """Placeholder context analyzer.

    Derives additional capabilities from the goal objective and enriches
    the context's available_capabilities.
    """

    _CAPABILITY_KEYWORDS: dict[str, str] = {
        "search": "data_search",
        "find": "data_search",
        "lookup": "data_search",
        "compute": "computation",
        "calculate": "computation",
        "analyze": "analytics",
        "report": "analytics",
        "summarise": "summarization",
        "summarize": "summarization",
        "translate": "translation",
        "convert": "translation",
    }

    async def analyze(
        self, goal: PlanningGoal, context: PlanningContext
    ) -> PlanningContext:
        """Enrich context with capabilities derived from the goal."""
        enriched = list(context.available_capabilities)
        for _keyword, capability in self._CAPABILITY_KEYWORDS.items():
            if capability not in enriched:
                enriched.append(capability)
        context.available_capabilities = enriched
        return context
