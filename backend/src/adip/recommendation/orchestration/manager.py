"""RecommendationManager — lightweight facade over the coordinator.

Provides a simplified interface for the RecommendationService,
delegating to the RecommendationCoordinator for orchestration.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid

import structlog

from adip.recommendation.contracts.models import (
    RecommendationHealth,
    RecommendationMetrics,
    RecommendationRequest,
    RecommendationResult,
)
from adip.recommendation.orchestration.coordinator import RecommendationCoordinator

log = structlog.get_logger(__name__)


class RecommendationManager:
    """Lightweight facade over the RecommendationCoordinator.

    Delegates recommendation execution to the coordinator and
    provides convenience methods for result retrieval, health,
    and metrics.
    """

    def __init__(
        self,
        coordinator: RecommendationCoordinator | None = None,
    ) -> None:
        self._coordinator = coordinator or RecommendationCoordinator()
        self._results: dict[str, RecommendationResult] = {}

    def execute_recommendation(
        self,
        request: RecommendationRequest,
        correlation_id: str = "",
    ) -> RecommendationResult:
        """Execute a recommendation operation.

        Args:
            request: The recommendation request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The recommendation result.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("manager.execute", request_id=str(request.request_id), cid=cid)
        result = self._coordinator.recommend(request, correlation_id=cid)
        self._results[str(result.result_id)] = result
        return result

    def get_result(self, result_id: str) -> RecommendationResult | None:
        """Retrieve a recommendation result by ID.

        Args:
            result_id: The result identifier.

        Returns:
            RecommendationResult if found, None otherwise.
        """
        return self._results.get(result_id)

    def get_health(self) -> RecommendationHealth:
        """Get the health status of the Recommendation Engine.

        Returns:
            RecommendationHealth with current component statuses.
        """
        return self._coordinator.health()

    def get_metrics(self) -> RecommendationMetrics:
        """Get aggregated metrics for the Recommendation Engine.

        Returns:
            RecommendationMetrics with current metric values.
        """
        return self._coordinator.metrics()
