"""AI Overview composition — aggregates AI/reasoning/recommendation data."""

from __future__ import annotations

from typing import Any

from adip.api.rest.composition.base import BaseCompositionService


class AIOverviewComposition(BaseCompositionService):
    """Aggregates AI-related data: reasoning, recommendations, explanations."""

    def get_name(self) -> str:
        return "ai_overview"

    def get_overview(self) -> dict[str, Any]:
        return {
            "active_reasoning_sessions": 0,
            "pending_recommendations": 0,
            "recent_explanations": [],
            "reasoning_confidence": 0.0,
            "recommendation_accuracy": 0.0,
            "explanation_coverage": 0.0,
        }
