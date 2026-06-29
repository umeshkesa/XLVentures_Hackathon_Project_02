"""DefaultExecutionService — the ONLY public API for the Action Engine.

Wraps auth callbacks, audit callbacks, integration hooks,
session lifecycle, correlation ID propagation, and DTO
conversion. All external modules MUST go through this service.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

import structlog

from adip.execution.contracts.models import (
    ExecutionHealth,
    ExecutionMetrics,
    ExecutionPackage,
    ExecutionRequest,
    ExecutionResult,
    ExecutionSession,
)
from adip.execution.dtos import ExecutionRequestDTO, ExecutionResponseDTO
from adip.execution.orchestration.manager import ExecutionManagerImpl
from adip.execution.services.hooks import IntegrationHooks
from adip.execution.services.hooks import hooks as global_hooks

log = structlog.get_logger(__name__)

AuthCallback = Callable[[str, str], bool]
AuditCallback = Callable[[str, str, str, dict[str, Any]], None]


class DefaultExecutionService:
    """Default implementation of the ExecutionService interface.

    This is the ONLY public API for execution operations.
    Wraps auth, audit, hooks, correlation, and session lifecycle.

    Args:
        manager: Optional ExecutionManagerImpl instance.
        hooks: Optional IntegrationHooks instance.
        auth_callback: Optional auth check callback.
        audit_callback: Optional audit logging callback.
    """

    def __init__(
        self,
        manager: ExecutionManagerImpl | None = None,
        hooks: IntegrationHooks | None = None,
        auth_callback: AuthCallback | None = None,
        audit_callback: AuditCallback | None = None,
    ) -> None:
        self._manager = manager or ExecutionManagerImpl()
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
        action: str,
        entity_id: str,
        user_id: str,
        details: dict[str, Any],
        correlation_id: str = "",
    ) -> None:
        """Log an audit entry.

        Args:
            action: The action being audited.
            entity_id: The entity identifier.
            user_id: The user performing the action.
            details: Additional audit details.
            correlation_id: Optional correlation ID.
        """
        if self._audit_callback is not None:
            self._audit_callback(action, entity_id, user_id, details)

    def _dto_to_request(self, dto: ExecutionRequestDTO) -> ExecutionRequest:
        """Convert a DTO to an internal domain model.

        Args:
            dto: The execution request DTO.

        Returns:
            The internal ExecutionRequest model.
        """
        return ExecutionRequest(
            request_id=dto.request_id,
            action_decision_id=dto.action_decision_id,
            execution_mode=dto.execution_mode,
            priority=dto.priority,
            domain=dto.domain,
            target=dto.target,
            metadata=dto.metadata,
        )

    def start_execution(
        self,
        request: ExecutionRequestDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ExecutionResponseDTO | None:
        """Submit an execution request.

        Args:
            request: The execution request DTO.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExecutionResponseDTO if authorized, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())

        if not self._check_auth(user_id, "execute", correlation_id=cid):
            log.warning("service.auth_failed", user_id=user_id, cid=cid)
            return None

        self._audit("start_execution", str(request.request_id), user_id, {}, correlation_id=cid)

        self._hooks.fire_pre_execute(str(request.request_id), correlation_id=cid)

        try:
            internal_request = self._dto_to_request(request)
            session = self._manager.start_execution(internal_request, correlation_id=cid)

            self._hooks.fire_session_created(str(session.session_id), correlation_id=cid)
            self._hooks.fire_post_execute(str(session.session_id), True, correlation_id=cid)

            self._audit("execution_started", str(session.session_id), user_id, {
                "request_id": str(request.request_id),
                "state": str(session.state),
            }, correlation_id=cid)

            response = ExecutionResponseDTO(
                request_id=request.request_id,
                session_id=session.session_id,
                state=session.state,
                execution_mode=request.execution_mode,
                message=f"Execution started with session {session.session_id}",
            )
            log.info(
                "service.execution_started",
                session_id=str(session.session_id),
                user_id=user_id,
                cid=cid,
            )
            return response

        except Exception as e:
            log.error("service.execution_error", error=str(e), cid=cid)
            self._hooks.fire_on_error(str(request.request_id), str(e), correlation_id=cid)
            self._audit("execution_error", str(request.request_id), user_id, {
                "error": str(e),
            }, correlation_id=cid)
            return None

    def get_session(
        self,
        session_id: str,
        correlation_id: str = "",
    ) -> ExecutionSession | None:
        """Retrieve an execution session by ID.

        Args:
            session_id: The session identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExecutionSession if found, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        return self._manager.get_session(session_id)

    def get_result(
        self,
        result_id: str,
        correlation_id: str = "",
    ) -> ExecutionResult | None:
        """Retrieve an execution result by ID.

        Args:
            result_id: The result identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExecutionResult if found, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        return self._manager.get_result(result_id)

    def get_package(
        self,
        package_id: str,
        correlation_id: str = "",
    ) -> ExecutionPackage | None:
        """Retrieve an execution package by ID.

        Args:
            package_id: The package identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExecutionPackage if found, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        return self._manager.get_package(package_id)

    def cancel_execution(
        self,
        session_id: str,
        reason: str = "",
        user_id: str = "",
        correlation_id: str = "",
    ) -> bool:
        """Cancel an active execution.

        Args:
            session_id: The session to cancel.
            reason: Optional reason for cancellation.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if cancelled successfully, False otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())

        if not self._check_auth(user_id, "cancel", correlation_id=cid):
            log.warning("service.cancel_auth_failed", user_id=user_id, cid=cid)
            return False

        self._audit("cancel_execution", session_id, user_id, {"reason": reason}, correlation_id=cid)

        result = self._manager.cancel_execution(session_id, reason)

        if result:
            self._hooks.fire_session_completed(session_id, "CANCELLED", correlation_id=cid)
            log.info("service.execution_cancelled", session_id=session_id, cid=cid)

        return result

    def get_health(
        self,
        correlation_id: str = "",
    ) -> ExecutionHealth:
        """Get the health status of the Action Engine.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExecutionHealth with current component statuses.
        """
        cid = correlation_id or str(uuid.uuid4())
        return self._manager.get_health()

    def get_metrics(
        self,
        correlation_id: str = "",
    ) -> ExecutionMetrics:
        """Get aggregated metrics for the Action Engine.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExecutionMetrics with current metric values.
        """
        cid = correlation_id or str(uuid.uuid4())
        return self._manager.get_metrics()
