"""DefaultRecommendationService — the ONLY public API.

Provides the external interface for recommendation operations
with authentication hooks, audit hooks, integration hooks,
structured logging, metrics, and correlation ID propagation.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

import structlog

from adip.recommendation.contracts.models import (
    RecommendationHealth,
    RecommendationMetrics,
    RecommendationRequest,
    RecommendationResult,
)
from adip.recommendation.dtos import (
    RecommendationPackageDTO,
    RecommendationRequestDTO,
    RecommendationResponseDTO,
)
from adip.recommendation.enums import (
    RecommendationDomain,
    RecommendationStrategy,
)
from adip.recommendation.orchestration.manager import RecommendationManager
from adip.recommendation.services.hooks import IntegrationHooks
from adip.recommendation.services.hooks import hooks as global_hooks

log = structlog.get_logger(__name__)


class DefaultRecommendationService:
    """Default implementation of the RecommendationService interface.

    This is the ONLY public API for all recommendation operations.
    Provides auth/audit hooks, integration hooks, structured logging,
    correlation ID propagation, and delegation to RecommendationManager.

    Deterministic placeholder implementation.
    """

    def __init__(
        self,
        manager: RecommendationManager | None = None,
        hooks: IntegrationHooks | None = None,
        auth_callback: Callable[[str, str], bool] | None = None,
        audit_callback: Callable[[str, str, str, dict[str, Any]], None] | None = None,
    ) -> None:
        self._manager = manager or RecommendationManager()
        self._hooks = hooks or global_hooks
        self._auth_callback = auth_callback
        self._audit_callback = audit_callback

    def recommend(
        self,
        request: RecommendationRequestDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> RecommendationResponseDTO | None:
        """Execute a recommendation operation.

        Args:
            request: The recommendation request DTO.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            RecommendationResponseDTO if authorized, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.recommend", request_id=request.reasoning_result_id, user=user_id, cid=cid)

        if self._auth_callback and user_id:
            if not self._auth_callback(user_id, "recommend"):
                log.warning("service.auth.failed", user=user_id)
                return None

        self._hooks.run_pre_recommend(request_id=request.reasoning_result_id, user_id=user_id)

        domain = request.domain if hasattr(request, 'domain') else RecommendationDomain.GENERAL
        strategy = request.strategy if hasattr(request, 'strategy') else RecommendationStrategy.NEXT_BEST_ACTION

        internal_request = RecommendationRequest(
            reasoning_result_id=uuid.UUID(request.reasoning_result_id) if isinstance(request.reasoning_result_id, str) else request.reasoning_result_id,
            domain=domain,
            strategy=strategy,
            context=request.context if hasattr(request, 'context') else {},
            metadata=request.metadata if hasattr(request, 'metadata') else {},
        )

        result = self._manager.execute_recommendation(internal_request, correlation_id=cid)

        if self._audit_callback:
            self._audit_callback(
                "recommend",
                user_id,
                str(result.result_id),
                {"status": result.status.value, "domain": domain.value},
            )

        self._hooks.run_post_recommend(
            result_id=str(result.result_id),
            status=result.status.value,
            user_id=user_id,
        )

        response = RecommendationResponseDTO(
            result_id=result.result_id,
            request_id=result.request_id,
            decision={
                "conclusion": result.decision.conclusion if result.decision else "",
                "confidence": result.decision.confidence if result.decision else 0.0,
                "readiness": result.readiness,
            },
            candidates_count=len(result.candidates),
            packages_count=1 if result.decision and result.decision.package else 0,
            confidence=result.decision.confidence if result.decision else 0.0,
            status=result.status,
            created_at=result.created_at,
        )

        log.info("service.recommend.complete", result_id=str(response.result_id), status=response.status.value)
        return response

    def get_result(
        self,
        result_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> RecommendationResult | None:
        """Retrieve a recommendation result by ID.

        Args:
            result_id: The result identifier.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            RecommendationResult if found and authorized, None otherwise.
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
    ) -> RecommendationPackageDTO | None:
        """Retrieve a recommendation package by ID.

        Args:
            package_id: The package identifier.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            RecommendationPackageDTO if found and authorized, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.get_package", package_id=package_id, user=user_id, cid=cid)
        return None

    def get_health(self, correlation_id: str = "") -> RecommendationHealth:
        """Get the health status of the Recommendation Engine.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            RecommendationHealth with current component statuses.
        """
        return self._manager.get_health()

    def get_metrics(self, correlation_id: str = "") -> RecommendationMetrics:
        """Get aggregated metrics for the Recommendation Engine.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            RecommendationMetrics with current metric values.
        """
        return self._manager.get_metrics()
