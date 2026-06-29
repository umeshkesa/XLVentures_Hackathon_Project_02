"""DefaultActionService — the ONLY public API for the Action Manager.

Wraps auth callbacks, audit callbacks, integration hooks,
session lifecycle, correlation ID propagation, and DTO
conversion. All external modules MUST go through this service.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

import structlog

from adip.actions.contracts.models import (
    ActionDecision,
    ActionHealth,
    ActionMetrics,
    ActionPlan,
    ActionRequest,
    ActionSession,
)
from adip.actions.dtos import ActionPlanDTO, ActionRequestDTO, ActionResponseDTO
from adip.actions.orchestration.manager import ActionManager
from adip.actions.services.hooks import IntegrationHooks
from adip.actions.services.hooks import hooks as global_hooks

log = structlog.get_logger(__name__)

AuthCallback = Callable[[str, str], bool]
AuditCallback = Callable[[str, str, str, dict[str, Any]], None]


class DefaultActionService:
    """Default implementation of the ActionService interface.

    This is the ONLY public API for action planning operations.
    Wraps auth, audit, hooks, correlation, and session lifecycle.

    Args:
        manager: Optional ActionManager instance.
        hooks: Optional IntegrationHooks instance.
        auth_callback: Optional auth check callback.
        audit_callback: Optional audit logging callback.
    """

    def __init__(
        self,
        manager: ActionManager | None = None,
        hooks: IntegrationHooks | None = None,
        auth_callback: AuthCallback | None = None,
        audit_callback: AuditCallback | None = None,
    ) -> None:
        self._manager = manager or ActionManager()
        self._hooks = hooks or global_hooks
        self._auth_callback = auth_callback
        self._audit_callback = audit_callback

    def _check_auth(
        self,
        user_id: str,
        permission: str,
        correlation_id: str = "",
    ) -> bool:
        """Check authorization.

        Args:
            user_id: The user identifier.
            permission: The permission to check.
            correlation_id: Optional correlation ID.

        Returns:
            True if authorized, False otherwise.
        """
        if self._auth_callback is None:
            return True
        return self._auth_callback(user_id, permission)

    def _audit(
        self,
        user_id: str,
        action: str,
        resource_id: str,
        details: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> None:
        """Log an audit entry.

        Args:
            user_id: The user identifier.
            action: The action being audited.
            resource_id: The resource identifier.
            details: Optional details.
            correlation_id: Optional correlation ID.
        """
        if self._audit_callback is not None:
            self._audit_callback(user_id, action, resource_id, details or {})

    def plan_action(
        self,
        request: ActionRequestDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ActionResponseDTO | None:
        """Submit an action planning request.

        Args:
            request: The action request DTO.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ActionResponseDTO if authorized, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())

        if not self._check_auth(user_id, "action:plan", cid):
            log.warning("service.auth.failed", user_id=user_id, cid=cid)
            return None

        self._hooks.run_pre_plan(request=request, cid=cid)

        internal_request = ActionRequest(
            request_id=request.request_id,
            review_decision_id=request.review_decision_id,
            action_type=request.action_type,
            priority=request.priority,
            domain=request.domain,
            target=request.target,
            metadata=request.metadata,
        )

        self._audit(
            user_id,
            "action.plan.started",
            str(internal_request.request_id),
            {"action_type": str(request.action_type)},
            cid,
        )

        try:
            decision = self._manager.start_planning(internal_request, correlation_id=cid)
        except Exception as e:
            log.error("service.plan.failed", error=str(e), cid=cid)
            self._hooks.run_on_error(error=str(e), cid=cid)
            raise

        self._hooks.run_post_plan(decision=decision, cid=cid)
        self._hooks.run_decision_made(decision=decision, cid=cid)

        self._audit(
            user_id,
            "action.plan.completed",
            str(decision.decision_id),
            {
                "ready": decision.is_ready,
                "issues": len(decision.issues),
            },
            cid,
        )

        plan_dto = None
        if decision.plan:
            plan_dto = ActionPlanDTO(
                plan_id=decision.plan.plan_id,
                request_id=internal_request.request_id,
                name=decision.plan.name,
                step_count=len(decision.plan.steps),
                has_rollback=decision.plan.rollback_plan is not None,
                status=decision.plan.status,
                readiness=decision.readiness,
            )

        session = self._manager.get_session(str(decision.decision_id))

        return ActionResponseDTO(
            request_id=internal_request.request_id,
            decision=plan_dto,
            session_id=session.session_id if session else uuid.uuid4(),
            status=str(decision.readiness.value) if decision.readiness else "COMPLETED",
            message=f"Action plan {'ready' if decision.is_ready else 'not ready'} for execution",
        )

    def get_decision(
        self,
        decision_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ActionDecision | None:
        """Retrieve an action decision by ID.

        Args:
            decision_id: The decision identifier.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ActionDecision if found and authorized, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        if not self._check_auth(user_id, "action:read", cid):
            return None
        return self._manager.get_decision(decision_id)

    def get_plan(
        self,
        plan_id: str,
        correlation_id: str = "",
    ) -> ActionPlan | None:
        """Retrieve an action plan by ID.

        Args:
            plan_id: The plan identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ActionPlan if found, None otherwise.
        """
        return self._manager.get_plan(plan_id)

    def get_session(
        self,
        session_id: str,
        correlation_id: str = "",
    ) -> ActionSession | None:
        """Retrieve an action session by ID.

        Args:
            session_id: The session identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ActionSession if found, None otherwise.
        """
        return self._manager.get_session(session_id)

    def get_health(
        self,
        correlation_id: str = "",
    ) -> ActionHealth:
        """Get the health status of the Action Manager.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ActionHealth with current component statuses.
        """
        return self._manager.get_health()

    def get_metrics(
        self,
        correlation_id: str = "",
    ) -> ActionMetrics:
        """Get aggregated metrics for the Action Manager.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ActionMetrics with current metric values.
        """
        return self._manager.get_metrics()
