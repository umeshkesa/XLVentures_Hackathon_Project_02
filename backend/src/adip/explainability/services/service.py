"""DefaultExplainabilityService — the ONLY public API.

Provides the external interface for explanation operations
with authentication hooks, audit hooks, integration hooks,
structured logging, metrics, and correlation ID propagation.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

import structlog

from adip.explainability.contracts.models import (
    ExplanationHealth,
    ExplanationMetrics,
    ExplanationRequest,
    ExplanationResult,
)
from adip.explainability.dtos import (
    ExplanationPackageDTO,
    ExplanationRequestDTO,
    ExplanationResponseDTO,
)
from adip.explainability.enums import ExplanationDomain, ExplanationLayer
from adip.explainability.orchestration.manager import ExplainabilityManagerImpl
from adip.explainability.services.hooks import IntegrationHooks
from adip.explainability.services.hooks import hooks as global_hooks

log = structlog.get_logger(__name__)


class DefaultExplainabilityService:
    """Default implementation of the ExplainabilityService interface.

    This is the ONLY public API for all explanation operations.
    Provides auth/audit hooks, integration hooks, structured logging,
    correlation ID propagation, and delegation to ExplainabilityManagerImpl.

    Deterministic placeholder implementation.
    """

    def __init__(
        self,
        manager: ExplainabilityManagerImpl | None = None,
        hooks: IntegrationHooks | None = None,
        auth_callback: Callable[[str, str], bool] | None = None,
        audit_callback: Callable[[str, str, str, dict[str, Any]], None] | None = None,
    ) -> None:
        self._manager = manager or ExplainabilityManagerImpl()
        self._hooks = hooks or global_hooks
        self._auth_callback = auth_callback
        self._audit_callback = audit_callback

    def explain(
        self,
        request: ExplanationRequestDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ExplanationResponseDTO | None:
        """Execute an explanation operation.

        Steps:
        1. Check auth (if auth_callback provided, returns None if not authorized)
        2. Convert DTO to domain model
        3. Fire pre_explain hook
        4. Call manager.execute_explanation()
        5. Fire post_explain hook
        6. Audit (if audit_callback provided)
        7. Convert to response DTO
        8. Wrap errors, fire on_error hook

        Args:
            request: The explanation request DTO.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExplanationResponseDTO if authorized, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.explain", reasoning_result_id=request.reasoning_result_id, user=user_id, cid=cid)

        if self._auth_callback and user_id:
            if not self._auth_callback(user_id, "explain"):
                log.warning("service.auth.failed", user=user_id)
                return None

        try:
            self._hooks.run_pre_explain(
                reasoning_result_id=request.reasoning_result_id,
                user_id=user_id,
                correlation_id=cid,
            )

            domain_str = request.domain if request.domain else "SYSTEM"
            domain = ExplanationDomain(domain_str) if domain_str in [e.value for e in ExplanationDomain] else ExplanationDomain.SYSTEM

            target_layers: list[ExplanationLayer] = []
            for a in request.target_audiences:
                try:
                    target_layers.append(ExplanationLayer(a))
                except ValueError:
                    target_layers.append(ExplanationLayer.ENGINEER)
            if not target_layers:
                target_layers.append(ExplanationLayer.ENGINEER)

            internal_request = ExplanationRequest(
                reasoning_result_id=uuid.UUID(request.reasoning_result_id) if isinstance(request.reasoning_result_id, str) else uuid.uuid4(),
                evidence_result_id=uuid.UUID(request.evidence_result_id) if request.evidence_result_id and isinstance(request.evidence_result_id, str) else uuid.uuid4(),
                recommendation_result_id=uuid.UUID(request.recommendation_result_id) if request.recommendation_result_id and isinstance(request.recommendation_result_id, str) else uuid.uuid4(),
                target_audiences=target_layers,
                domain=domain,
                context=request.context,
                metadata=request.metadata,
            )

            result = self._manager.execute_explanation(internal_request, correlation_id=cid)

            if self._audit_callback:
                self._audit_callback(
                    "explain",
                    user_id,
                    str(result.result_id),
                    {"status": result.status.value, "domain": domain.value},
                )

            self._hooks.run_post_explain(
                result_id=str(result.result_id),
                status=result.status.value,
                request_id=request.reasoning_result_id,
                user_id=user_id,
            )

            package_id = str(result.package.package_id) if result.package else ""

            response = ExplanationResponseDTO(
                result_id=result.result_id,
                request_id=result.request_id,
                package_id=package_id,
                narratives_count=len(result.narratives),
                citations_count=len(result.citations),
                confidence=result.confidence.overall_confidence if result.confidence else 0.0,
                status=result.status.value,
                created_at=result.created_at,
            )

            log.info("service.explain.complete", result_id=str(response.result_id), status=response.status)
            return response

        except Exception as e:
            log.error("service.explain.error", error=str(e), user=user_id, cid=cid)
            self._hooks.run_on_error(
                request=request,
                error=e,
                user_id=user_id,
                correlation_id=cid,
            )
            return None

    def get_result(
        self,
        result_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ExplanationResult | None:
        """Retrieve an explanation result by ID.

        Args:
            result_id: The result identifier.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExplanationResult if found and authorized, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.get_result", result_id=result_id, user=user_id, cid=cid)

        if self._auth_callback and user_id:
            if not self._auth_callback(user_id, "get_result"):
                return None

        result = self._manager.get_result(result_id)

        if result and self._audit_callback:
            self._audit_callback("get_result", user_id, result_id, {})

        return result

    def get_package(
        self,
        package_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ExplanationPackageDTO | None:
        """Retrieve an explanation package by ID.

        Args:
            package_id: The package identifier.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExplanationPackageDTO if found and authorized, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.get_package", package_id=package_id, user=user_id, cid=cid)
        return None

    def get_health(self, correlation_id: str = "") -> ExplanationHealth:
        """Get the health status of the Explainability Engine.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExplanationHealth with current component statuses.
        """
        return self._manager.get_health()

    def get_metrics(self, correlation_id: str = "") -> ExplanationMetrics:
        """Get aggregated metrics for the Explainability Engine.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExplanationMetrics with current metric values.
        """
        return self._manager.get_metrics()
