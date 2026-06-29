"""ReasoningManager — lightweight internal orchestrator.

Facade over ReasoningCoordinator. Validates operations, delegates
orchestration to the coordinator, and stores results.

ReasoningManager remains lightweight — no business logic lives here.
"""

from __future__ import annotations

import structlog

from adip.reasoning.contracts.models import (
    ReasoningHealth,
    ReasoningMetrics,
    ReasoningRequest,
    ReasoningResult,
)
from adip.reasoning.orchestration.coordinator import ReasoningCoordinator

log = structlog.get_logger(__name__)


class ReasoningManager:
    """Lightweight internal orchestrator for all reasoning operations."""

    def __init__(self, coordinator: ReasoningCoordinator | None = None) -> None:
        self._coordinator = coordinator or ReasoningCoordinator()

    def execute_reasoning(
        self,
        request: ReasoningRequest,
        correlation_id: str = "",
    ) -> ReasoningResult:
        """Execute a reasoning operation."""
        log.info(
            "reasoning_manager.execute",
            request_id=str(request.request_id),
            correlation_id=correlation_id,
        )
        return self._coordinator.reason(request, correlation_id=correlation_id)

    def get_result(self, result_id: str) -> ReasoningResult | None:
        """Retrieve a reasoning result by ID."""
        return self._coordinator.get_result(result_id)

    def get_health(self) -> ReasoningHealth:
        """Return the current health status."""
        return self._coordinator.health()

    def get_metrics(self) -> ReasoningMetrics:
        """Return aggregated metrics."""
        return self._coordinator.metrics()
