"""Orchestration layer for the Recommendation Engine Phase 3.5.

Coordinates the full recommendation pipeline by delegating to
Phase 2 execution components and Phase 3/3.5 orchestration components.
"""
from __future__ import annotations

from adip.recommendation.orchestration.approval_readiness import (
    ApprovalReadinessResult,
    RecommendationApprovalReadiness,
)
from adip.recommendation.orchestration.confidence import RecommendationConfidenceCalculator
from adip.recommendation.orchestration.coordinator import RecommendationCoordinator
from adip.recommendation.orchestration.justification import (
    JustificationRecord,
    RecommendationJustification,
)
from adip.recommendation.orchestration.lineage import RecommendationLineage
from adip.recommendation.orchestration.manager import RecommendationManager
from adip.recommendation.orchestration.portfolio_comparator import PortfolioComparator
from adip.recommendation.orchestration.portfolio_quality import (
    PortfolioQuality,
    PortfolioQualityResult,
)
from adip.recommendation.orchestration.quality import QualityResult, RecommendationQualityManager
from adip.recommendation.orchestration.readiness import RecommendationReadiness
from adip.recommendation.orchestration.review import RecommendationReview
from adip.recommendation.orchestration.session import RecommendationSessionManager
from adip.recommendation.orchestration.snapshot import RecommendationSnapshot
from adip.recommendation.orchestration.version_manager import RecommendationVersionManager

__all__ = [
    "RecommendationSessionManager",
    "RecommendationConfidenceCalculator",
    "RecommendationReview",
    "RecommendationVersionManager",
    "RecommendationReadiness",
    "RecommendationLineage",
    "RecommendationSnapshot",
    "PortfolioComparator",
    "RecommendationCoordinator",
    "RecommendationManager",
    "RecommendationQualityManager",
    "QualityResult",
    "RecommendationJustification",
    "JustificationRecord",
    "RecommendationApprovalReadiness",
    "ApprovalReadinessResult",
    "PortfolioQuality",
    "PortfolioQualityResult",
]
