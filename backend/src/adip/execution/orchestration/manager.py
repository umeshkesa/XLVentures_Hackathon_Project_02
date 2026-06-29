"""ExecutionManagerImpl — lightweight facade over the coordinator.

Provides a simplified interface for the ExecutionService,
delegating to the ExecutionCoordinatorImpl for orchestration.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid

import structlog

from adip.execution.contracts.models import (
    ExecutionDecision,
    ExecutionHealth,
    ExecutionMetrics,
    ExecutionPackage,
    ExecutionRequest,
    ExecutionResult,
    ExecutionSession,
)
from adip.execution.orchestration.coordinator import ExecutionCoordinatorImpl

log = structlog.get_logger(__name__)


class ExecutionManagerImpl:
    """Lightweight facade over the ExecutionCoordinatorImpl.

    Delegates execution operations to the coordinator and
    provides convenience methods for decision retrieval, health,
    metrics, and governance components.
    """

    def __init__(
        self,
        coordinator: ExecutionCoordinatorImpl | None = None,
    ) -> None:
        self._coordinator = coordinator or ExecutionCoordinatorImpl()
        self._decisions: dict[str, ExecutionDecision] = {}

    def start_execution(
        self,
        request: ExecutionRequest,
        correlation_id: str = "",
    ) -> ExecutionSession:
        """Start an execution operation.

        Args:
            request: The execution request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created execution session.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("manager.start_execution", request_id=str(request.request_id), cid=cid)

        result = self._coordinator.execute(request, correlation_id=cid)
        session = self._coordinator.get_session(str(result.session_id))

        decision = self._coordinator.get_decision(
            str(result.metadata.get("decision_id", ""))
        ) if result.metadata else None
        if decision:
            self._decisions[str(decision.decision_id)] = decision

        if session is None:
            log.error("manager.session_not_found", session_id=str(result.session_id))
            raise RuntimeError(f"Session {result.session_id} not found after execution")

        return session

    def get_session(self, session_id: str) -> ExecutionSession | None:
        """Retrieve an execution session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            ExecutionSession if found, None otherwise.
        """
        return self._coordinator.get_session(session_id)

    def get_result(self, result_id: str) -> ExecutionResult | None:
        """Retrieve an execution result by ID.

        Args:
            result_id: The result identifier.

        Returns:
            ExecutionResult if found, None otherwise.
        """
        return self._coordinator.get_result(result_id)

    def get_package(self, package_id: str) -> ExecutionPackage | None:
        """Retrieve an execution package by ID.

        Args:
            package_id: The package identifier.

        Returns:
            ExecutionPackage if found, None otherwise.
        """
        return self._coordinator.get_package(package_id)

    def cancel_execution(
        self,
        session_id: str,
        reason: str = "",
    ) -> bool:
        """Cancel an active execution.

        Args:
            session_id: The session to cancel.
            reason: Optional reason for cancellation.

        Returns:
            True if cancelled successfully, False otherwise.
        """
        return self._coordinator.cancel(session_id, reason)

    def get_health(self) -> ExecutionHealth:
        """Get the health status of the Action Engine.

        Returns:
            ExecutionHealth with current component statuses.
        """
        return self._coordinator.health()

    def get_metrics(self) -> ExecutionMetrics:
        """Get aggregated metrics for the Action Engine.

        Returns:
            ExecutionMetrics with current metric values.
        """
        return self._coordinator.metrics()

    def get_decision(self, decision_id: str) -> ExecutionDecision | None:
        """Retrieve an execution decision by ID.

        Args:
            decision_id: The decision identifier.

        Returns:
            ExecutionDecision if found, None otherwise.
        """
        if decision_id in self._decisions:
            return self._decisions[decision_id]
        return self._coordinator.get_decision(decision_id)
