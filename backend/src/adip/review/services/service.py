"""DefaultReviewService — the ONLY public API.

Provides the external interface for review operations
with authentication hooks, audit hooks, integration hooks,
structured logging, metrics, and correlation ID propagation.

Phase 3 adds governance confidence, readiness, audit package,
lineage, and delegation access methods.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from typing import Any

import structlog

from adip.review.contracts.models import (
    GovernanceAuditPackage as GovernanceAuditPackageModel,
)
from adip.review.contracts.models import (
    GovernanceLineage as GovernanceLineageModel,
)
from adip.review.contracts.models import (
    ReviewDecision,
    ReviewHealth,
    ReviewMetrics,
    ReviewRequest,
)
from adip.review.contracts.models import (
    ReviewReadiness as ReviewReadinessModel,
)
from adip.review.dtos import ReviewRequestDTO, ReviewResponseDTO
from adip.review.enums import ReviewStatus
from adip.review.orchestration.manager import ReviewManager
from adip.review.services.hooks import IntegrationHooks
from adip.review.services.hooks import hooks as global_hooks

log = structlog.get_logger(__name__)


class DefaultReviewService:
    """Default implementation of the DecisionReviewService interface.

    This is the ONLY public API for all review operations.
    Provides auth/audit hooks, integration hooks, structured logging,
    correlation ID propagation, and delegation to ReviewManager.

    Phase 3 adds governance queries: governance confidence, readiness,
    audit packages, lineage, and delegation records.

    Deterministic placeholder implementation.
    """

    def __init__(
        self,
        manager: ReviewManager | None = None,
        hooks: IntegrationHooks | None = None,
        auth_callback: Callable[[str, str], bool] | None = None,
        audit_callback: Callable[[str, str, str, dict[str, Any]], None] | None = None,
    ) -> None:
        self._manager = manager or ReviewManager()
        self._hooks = hooks or global_hooks
        self._auth_callback = auth_callback
        self._audit_callback = audit_callback

    def submit_review(
        self,
        request: ReviewRequestDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ReviewResponseDTO | None:
        """Submit a review request for processing.

        Steps:
        1. Check auth (if auth_callback provided, returns None if not authorized)
        2. Convert DTO to domain model
        3. Fire pre_review hook
        4. Call manager.start_review()
        5. Fire post_review hook
        6. Audit (if audit_callback provided)
        7. Convert to response DTO
        8. Wrap errors, fire on_error hook

        Args:
            request: The review request DTO.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReviewResponseDTO if authorized, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info(
            "service.submit_review",
            rec_decision_id=str(request.recommendation_decision_id),
            user=user_id,
            cid=cid,
        )

        if self._auth_callback and user_id:
            if not self._auth_callback(user_id, "submit_review"):
                log.warning("service.auth.failed", user=user_id)
                return None

        try:
            self._hooks.run_pre_review(
                recommendation_decision_id=str(request.recommendation_decision_id),
                explanation_decision_id=str(request.explanation_decision_id),
                user_id=user_id,
                correlation_id=cid,
            )

            internal_request = ReviewRequest(
                recommendation_decision_id=request.recommendation_decision_id,
                explanation_decision_id=request.explanation_decision_id,
                domain=request.domain,
                priority=request.priority,
                deadline=request.deadline,
                metadata=request.metadata,
            )

            decision = self._manager.start_review(internal_request, correlation_id=cid)

            if self._audit_callback:
                self._audit_callback(
                    "submit_review",
                    user_id,
                    str(decision.decision_id),
                    {"outcome": decision.outcome.value, "domain": request.domain.value},
                )

            self._hooks.run_post_review(
                decision_id=str(decision.decision_id),
                outcome=decision.outcome.value,
                request_id=str(request.request_id),
                user_id=user_id,
            )

            response = ReviewResponseDTO(
                request_id=request.request_id,
                decision=None,
                session_id=uuid.uuid4(),
                status=ReviewStatus.COMPLETED,
                message=f"Review completed with outcome: {decision.outcome.value}",
            )

            log.info(
                "service.submit_review.complete",
                decision_id=str(decision.decision_id),
                outcome=decision.outcome.value,
            )
            return response

        except Exception as e:
            log.error("service.submit_review.error", error=str(e), user=user_id, cid=cid)
            self._hooks.run_on_error(
                request=request,
                error=e,
                user_id=user_id,
                correlation_id=cid,
            )
            return None

    def get_decision(
        self,
        decision_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ReviewDecision | None:
        """Retrieve a review decision by ID.

        Args:
            decision_id: The decision identifier.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReviewDecision if found and authorized, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.get_decision", decision_id=decision_id, user=user_id, cid=cid)

        if self._auth_callback and user_id:
            if not self._auth_callback(user_id, "get_decision"):
                return None

        decision = self._manager.get_decision(decision_id)

        if decision and self._audit_callback:
            self._audit_callback("get_decision", user_id, decision_id, {})

        return decision

    def get_session(
        self,
        session_id: str,
        correlation_id: str = "",
    ) -> Any | None:
        """Retrieve a review session by ID.

        Args:
            session_id: The session identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReviewSession if found, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.get_session", session_id=session_id, cid=cid)
        return self._manager.get_session(session_id)

    def get_health(self, correlation_id: str = "") -> ReviewHealth:
        """Get the health status of the Decision Review Layer.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReviewHealth with current component statuses.
        """
        log.info("service.get_health", correlation_id=correlation_id or "")
        return self._manager.get_health()

    def get_metrics(self, correlation_id: str = "") -> ReviewMetrics:
        """Get aggregated metrics for the Decision Review Layer.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReviewMetrics with current metric values.
        """
        log.info("service.get_metrics", correlation_id=correlation_id or "")
        return self._manager.get_metrics()

    def get_readiness(
        self,
        readiness_id: str,
        correlation_id: str = "",
    ) -> ReviewReadinessModel | None:
        """Get a readiness assessment by ID.

        Args:
            readiness_id: The readiness identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReviewReadinessModel if found, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.get_readiness", readiness_id=readiness_id, cid=cid)
        return self._manager.get_readiness(readiness_id)

    def get_audit_package(
        self,
        package_id: str,
        correlation_id: str = "",
    ) -> GovernanceAuditPackageModel | None:
        """Get an audit package by ID.

        Args:
            package_id: The package identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            GovernanceAuditPackageModel if found, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.get_audit_package", package_id=package_id, cid=cid)
        return self._manager.get_audit_package(package_id)

    def get_lineage(
        self,
        lineage_id: str,
        correlation_id: str = "",
    ) -> GovernanceLineageModel | None:
        """Get a lineage record by ID.

        Args:
            lineage_id: The lineage identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            GovernanceLineageModel if found, None otherwise.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("service.get_lineage", lineage_id=lineage_id, cid=cid)
        return self._manager.get_lineage(lineage_id)

    @property
    def manager(self) -> ReviewManager:
        """Get the underlying manager."""
        return self._manager

    @property
    def hooks(self) -> IntegrationHooks:
        """Get the integration hooks instance."""
        return self._hooks
