"""ActionManager — lightweight facade over the coordinator.

Provides a simplified interface for the ActionService,
delegating to the ActionCoordinator for orchestration.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid

import structlog

from adip.actions.contracts.models import (
    ActionDecision,
    ActionHealth,
    ActionMetrics,
    ActionPlan,
    ActionRequest,
    ActionSession,
)
from adip.actions.orchestration.coordinator import ActionCoordinator

log = structlog.get_logger(__name__)


class ActionManager:
    """Lightweight facade over the ActionCoordinator.

    Delegates action planning execution to the coordinator and
    provides convenience methods for decision retrieval, health,
    metrics, and Phase 3 governance components.
    """

    def __init__(
        self,
        coordinator: ActionCoordinator | None = None,
    ) -> None:
        self._coordinator = coordinator or ActionCoordinator()
        self._decisions: dict[str, ActionDecision] = {}

    def start_planning(
        self,
        request: ActionRequest,
        correlation_id: str = "",
    ) -> ActionDecision:
        """Start an action planning operation.

        Args:
            request: The action request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The action decision.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("manager.start_planning", request_id=str(request.request_id), cid=cid)
        decision = self._coordinator.plan(request, correlation_id=cid)
        self._decisions[str(decision.decision_id)] = decision
        return decision

    def get_decision(self, decision_id: str) -> ActionDecision | None:
        """Retrieve an action decision by ID.

        Args:
            decision_id: The decision identifier.

        Returns:
            ActionDecision if found, None otherwise.
        """
        if decision_id in self._decisions:
            return self._decisions[decision_id]
        return self._coordinator.get_decision(decision_id)

    def get_plan(self, plan_id: str) -> ActionPlan | None:
        """Retrieve an action plan by ID.

        Args:
            plan_id: The plan identifier.

        Returns:
            ActionPlan if found, None otherwise.
        """
        return self._coordinator.get_plan(plan_id)

    def get_session(self, session_id: str) -> ActionSession | None:
        """Retrieve an action session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            ActionSession if found, None otherwise.
        """
        return self._coordinator.session_manager.get_session(session_id)

    def get_health(self) -> ActionHealth:
        """Get the health status of the Action Manager.

        Returns:
            ActionHealth with current component statuses.
        """
        return self._coordinator.health()

    def get_metrics(self) -> ActionMetrics:
        """Get aggregated metrics for the Action Manager.

        Returns:
            ActionMetrics with current metric values.
        """
        return self._coordinator.metrics()
