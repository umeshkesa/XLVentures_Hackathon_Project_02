"""ReviewManager — lightweight facade over the coordinator.

Provides a simplified interface for the ReviewService,
delegating to the ReviewCoordinator for orchestration.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog

from adip.review.contracts.models import (
    GovernanceAuditPackage as GovernanceAuditPackageModel,
)
from adip.review.contracts.models import (
    GovernanceConfidence,
    ReviewDecision,
    ReviewHealth,
    ReviewMetrics,
    ReviewRequest,
)
from adip.review.contracts.models import (
    GovernanceLineage as GovernanceLineageModel,
)
from adip.review.contracts.models import (
    ReviewReadiness as ReviewReadinessModel,
)
from adip.review.orchestration.coordinator import ReviewCoordinator

log = structlog.get_logger(__name__)


class ReviewManager:
    """Lightweight facade over the ReviewCoordinator.

    Delegates review execution to the coordinator and
    provides convenience methods for decision retrieval, health,
    metrics, and Phase 3 governance components.
    """

    def __init__(
        self,
        coordinator: ReviewCoordinator | None = None,
    ) -> None:
        self._coordinator = coordinator or ReviewCoordinator()
        self._decisions: dict[str, ReviewDecision] = {}

    def start_review(
        self,
        request: ReviewRequest,
        correlation_id: str = "",
    ) -> ReviewDecision:
        """Start a review operation.

        Args:
            request: The review request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The review decision.
        """
        cid = correlation_id or str(uuid.uuid4())
        log.info("manager.start_review", request_id=str(request.request_id), cid=cid)
        decision = self._coordinator.review(request, correlation_id=cid)
        self._decisions[str(decision.decision_id)] = decision
        return decision

    def get_decision(self, decision_id: str) -> ReviewDecision | None:
        """Retrieve a review decision by ID.

        Args:
            decision_id: The decision identifier.

        Returns:
            ReviewDecision if found, None otherwise.
        """
        return self._decisions.get(decision_id)

    def get_session(self, session_id: str) -> Any:
        """Retrieve a review session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            ReviewSession if found, None otherwise.
        """
        return self._coordinator.session_manager.get_session(session_id)

    def get_health(self) -> ReviewHealth:
        """Get the health status of the Decision Review Layer.

        Returns:
            ReviewHealth with current component statuses.
        """
        return self._coordinator.health()

    def get_metrics(self) -> ReviewMetrics:
        """Get aggregated metrics for the Decision Review Layer.

        Returns:
            ReviewMetrics with current metric values.
        """
        return self._coordinator.metrics()

    def get_governance_confidence(self) -> GovernanceConfidence | None:
        """Get the latest governance confidence calculation.

        Returns:
            GovernanceConfidence if available, None otherwise.
        """
        return None

    def get_readiness(self, readiness_id: str) -> ReviewReadinessModel | None:
        """Get a readiness assessment by ID.

        Args:
            readiness_id: The readiness identifier.

        Returns:
            ReviewReadinessModel if found, None otherwise.
        """
        return self._coordinator.readiness.get_readiness(readiness_id)

    def get_audit_package(self, package_id: str) -> GovernanceAuditPackageModel | None:
        """Get an audit package by ID.

        Args:
            package_id: The package identifier.

        Returns:
            GovernanceAuditPackageModel if found, None otherwise.
        """
        return self._coordinator.audit_package.get_package(package_id)

    def get_lineage(self, lineage_id: str) -> GovernanceLineageModel | None:
        """Get a lineage record by ID.

        Args:
            lineage_id: The lineage identifier.

        Returns:
            GovernanceLineageModel if found, None otherwise.
        """
        return self._coordinator.lineage.get_lineage(lineage_id)

    @property
    def coordinator(self) -> ReviewCoordinator:
        """Get the underlying coordinator."""
        return self._coordinator
