"""ExplainabilityManagerImpl — lightweight facade over the coordinator.

Provides a simplified interface for the ExplainabilityService,
delegating to the ExplainabilityCoordinatorImpl for orchestration.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid

import structlog

from adip.explainability.contracts.models import (
    ExplanationHealth,
    ExplanationMetrics,
    ExplanationRequest,
    ExplanationResult,
)
from adip.explainability.orchestration.coordinator import ExplainabilityCoordinatorImpl

log = structlog.get_logger(__name__)


class ExplainabilityManagerImpl:
    """Lightweight facade over the ExplainabilityCoordinatorImpl.

    Delegates explanation execution to the coordinator and
    provides convenience methods for result retrieval, health,
    and metrics.
    """

    def __init__(
        self,
        coordinator: ExplainabilityCoordinatorImpl | None = None,
    ) -> None:
        self._coordinator = coordinator or ExplainabilityCoordinatorImpl()
        self._results: dict[str, ExplanationResult] = {}

    def execute_explanation(
        self,
        request: ExplanationRequest,
        correlation_id: str = "",
    ) -> ExplanationResult:
        """Execute an explanation operation.

        Args:
            request: The explanation request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The explanation result.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("manager.execute", request_id=str(request.request_id), cid=cid)
        result = self._coordinator.explain(request, correlation_id=cid)
        self._results[str(result.result_id)] = result
        return result

    def get_result(self, result_id: str) -> ExplanationResult | None:
        """Retrieve an explanation result by ID.

        Args:
            result_id: The result identifier.

        Returns:
            ExplanationResult if found, None otherwise.
        """
        return self._results.get(result_id)

    def get_health(self) -> ExplanationHealth:
        """Get the health status of the Explainability Engine.

        Returns:
            ExplanationHealth with current component statuses.
        """
        return self._coordinator.health()

    def get_metrics(self) -> ExplanationMetrics:
        """Get aggregated metrics for the Explainability Engine.

        Returns:
            ExplanationMetrics with current metric values.
        """
        return self._coordinator.metrics()
