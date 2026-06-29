"""Service layer for the Decision Review Layer Phase 3.

Exports:
- DefaultReviewService (ONLY public API)
- IntegrationHooks + global hooks singleton
"""

from adip.review.services.hooks import IntegrationHooks, hooks
from adip.review.services.service import DefaultReviewService

__all__ = [
    "DefaultReviewService",
    "IntegrationHooks",
    "hooks",
]
