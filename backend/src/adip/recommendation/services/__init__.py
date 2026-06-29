"""Service layer for the Recommendation Engine Phase 3.

Provides the ONLY public API (RecommendationService) and integration hooks.
"""
from __future__ import annotations

from adip.recommendation.services.hooks import IntegrationHooks, hooks
from adip.recommendation.services.service import DefaultRecommendationService

__all__ = [
    "IntegrationHooks",
    "hooks",
    "DefaultRecommendationService",
]
