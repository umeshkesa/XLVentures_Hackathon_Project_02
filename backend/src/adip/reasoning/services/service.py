"""ReasoningService — the ONLY public API for enterprise reasoning operations.

Responsible for:
• Request validation
• Authentication & authorisation hooks
• Audit hook
• Logging & metrics
• Correlation ID propagation
• Session management
• Delegation to ReasoningManager

All external modules (Planner, Workflow Engine, etc.)
MUST go through ReasoningService. ReasoningManager is internal-only.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

import structlog

from adip.reasoning.contracts.models import (
    ReasoningHealth,
    ReasoningMetrics,
    ReasoningRequest,
    ReasoningResult,
)
from adip.reasoning.dtos import ReasoningRequestDTO, ReasoningResponseDTO
from adip.reasoning.execution.metrics import ReasoningMetricsCollector
from adip.reasoning.orchestration.manager import ReasoningManager
from adip.reasoning.orchestration.session import ReasoningSessionManager
from adip.reasoning.services.hooks import IntegrationHooks
from adip.reasoning.services.hooks import hooks as default_hooks

log = structlog.get_logger(__name__)


class AuthResult:
    """Result of an authentication/authorisation check."""

    def __init__(self, allowed: bool = True, reason: str = "") -> None:
        self.allowed = allowed
        self.reason = reason


class ReasoningService:
    """Enterprise facade for all reasoning operations.

    This is the ONLY public API. External modules MUST use this class
    to interact with the Reasoning Engine.

    ReasoningService must never call execution components directly.
    """

    def __init__(
        self,
        manager: ReasoningManager | None = None,
        hooks: IntegrationHooks | None = None,
        session_manager: ReasoningSessionManager | None = None,
        metrics_collector: ReasoningMetricsCollector | None = None,
        auth_callback: Callable[[str, str], AuthResult] | None = None,
        audit_callback: Callable[[str, str, str, dict[str, Any]], None] | None = None,
    ) -> None:
        self._manager = manager or ReasoningManager()
        self._hooks = hooks or default_hooks
        self._session_manager = session_manager or ReasoningSessionManager()
        self._metrics = metrics_collector or ReasoningMetricsCollector()
        self._auth_callback = auth_callback
        self._audit_callback = audit_callback

    def _audit(self, operation: str, entity_id: str, user_id: str, details: dict[str, Any]) -> None:
        if self._audit_callback:
            self._audit_callback(operation, entity_id, user_id, details)

    # ── Reasoning Operations ────────────────────────────────────────────

    def reason(
        self,
        request_dto: ReasoningRequestDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ReasoningResponseDTO | None:
        """Validate, authorise, and execute a reasoning operation.

        Args:
            request_dto: The reasoning request DTO.
            user_id: Optional user identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReasoningResponseDTO if authorised, None otherwise.
        """
        correlation_id = correlation_id or str(uuid.uuid4())
        log.info(
            "service.reason",
            evidence_package_id=str(request_dto.evidence_package_id),
            user_id=user_id,
            correlation_id=correlation_id,
        )

        if self._auth_callback:
            auth = self._auth_callback(user_id, "reason")
            if not auth.allowed:
                raise PermissionError(f"Reason not allowed: {auth.reason}")

        # Convert DTO to internal model
        internal_request = ReasoningRequest(
            evidence_package_id=request_dto.evidence_package_id,
            domain=request_dto.domain,
            strategy=request_dto.strategy,
            context=request_dto.context,
            metadata=request_dto.metadata,
        )

        # Create reasoning session
        session = self._session_manager.create_session(
            request_id=str(internal_request.request_id),
            domain=internal_request.domain,
            user_id=user_id,
            correlation_id=correlation_id,
            strategy_type=internal_request.strategy,
        )
        self._hooks.invoke_session_started(session)

        try:
            self._hooks.invoke_pre_reason(internal_request)

            result = self._manager.execute_reasoning(
                internal_request,
                correlation_id=correlation_id,
            )

            self._hooks.invoke_post_reason(result)

            # Update session
            self._session_manager.update_session_metadata(
                str(session.session_id),
                "hypotheses_count",
                len(result.hypotheses),
            )
            self._session_manager.update_session_metadata(
                str(session.session_id),
                "inferences_count",
                len(result.inferences),
            )
            self._session_manager.update_session_metadata(
                str(session.session_id),
                "contradictions_count",
                len(result.contradictions),
            )
            self._session_manager.update_session_metadata(
                str(session.session_id),
                "decisions_count",
                1 if result.decision else 0,
            )

            self._session_manager.complete_session(str(session.session_id))
            self._hooks.invoke_session_completed(session)

            self._audit("reason", str(result.result_id), user_id, {
                "correlation_id": correlation_id,
                "domain": internal_request.domain.value,
                "strategy": internal_request.strategy.value,
                "hypotheses": len(result.hypotheses),
                "inferences": len(result.inferences),
                "contradictions": len(result.contradictions),
                "status": result.status.value,
            })

            # Build response DTO
            response = ReasoningResponseDTO(
                result_id=result.result_id,
                request_id=result.request_id,
                decision=result.decision.model_dump() if result.decision else {},
                hypotheses_count=len(result.hypotheses),
                inferences_count=len(result.inferences),
                contradictions_count=len(result.contradictions),
                confidence=result.confidence.overall_confidence if result.confidence else 0.0,
                status=result.status,
                metadata=result.metadata,
            )

            return response

        except Exception as e:
            self._session_manager.complete_session(str(session.session_id))
            self._hooks.invoke_error("reason", e)
            self._audit("reason_error", str(internal_request.request_id), user_id, {
                "correlation_id": correlation_id,
                "error": str(e),
            })
            raise

    def get_result(
        self,
        result_id: str,
        user_id: str = "",
    ) -> ReasoningResult | None:
        """Retrieve a reasoning result by ID.

        Args:
            result_id: The result identifier.
            user_id: Optional user identifier for auth.

        Returns:
            ReasoningResult if found, None otherwise.
        """
        log.info("service.get_result", result_id=result_id, user_id=user_id)

        if self._auth_callback:
            auth = self._auth_callback(user_id, "get_result")
            if not auth.allowed:
                raise PermissionError(f"Get result not allowed: {auth.reason}")

        return self._manager.get_result(result_id)

    # ── Health & Metrics ──────────────────────────────────────────────

    def get_health(self, correlation_id: str = "") -> ReasoningHealth:
        """Return the current health status of the reasoning platform.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReasoningHealth with current component statuses.
        """
        log.info("service.health", correlation_id=correlation_id)
        return self._manager.get_health()

    def get_metrics(self, correlation_id: str = "") -> ReasoningMetrics:
        """Return aggregated reasoning platform metrics.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReasoningMetrics with current metric values.
        """
        log.info("service.get_metrics", correlation_id=correlation_id)
        return self._manager.get_metrics()
