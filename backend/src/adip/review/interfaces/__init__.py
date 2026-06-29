# INTERFACES FROZEN — Phase 1 (confirmed Phase 3.5)
# Do not add, remove, or modify abstract methods.
# Do not add, remove, or modify interface classes.
# Any change requires full ADIP RFC process approval.
# Phase 3.5 verification: All interfaces remain unchanged.

"""Abstract interfaces for the Decision Review Layer.

Defines all abstract interfaces used across review operations
following the Dependency Inversion Principle. All interfaces
are frozen after Phase 1.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from adip.review.contracts.models import (
    ApprovalWorkflow,
    EscalationRule,
    ReviewAudit,
    ReviewDecision,
    ReviewHealth,
    ReviewMetrics,
    ReviewPolicy,
    ReviewRequest,
    ReviewSession,
)
from adip.review.dtos import ReviewRequestDTO, ReviewResponseDTO
from adip.review.enums import ApprovalWorkflowType, ReviewerRole, ReviewOutcome, ReviewStatus


class DecisionReviewService(ABC):
    """Service-layer interface for the Decision Review Layer.

    This is the ONLY public API for external consumers.
    All review operations MUST go through this interface.
    """

    @abstractmethod
    def submit_review(
        self,
        request: ReviewRequestDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ReviewResponseDTO | None:
        """Submit a review request for processing.

        Args:
            request: The review request DTO.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReviewResponseDTO if authorized, None otherwise.
        """
        ...

    @abstractmethod
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
        ...

    @abstractmethod
    def get_session(
        self,
        session_id: str,
        correlation_id: str = "",
    ) -> ReviewSession | None:
        """Retrieve a review session by ID.

        Args:
            session_id: The session identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReviewSession if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_health(
        self,
        correlation_id: str = "",
    ) -> ReviewHealth:
        """Get the health status of the Decision Review Layer.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReviewHealth with current component statuses.
        """
        ...

    @abstractmethod
    def get_metrics(
        self,
        correlation_id: str = "",
    ) -> ReviewMetrics:
        """Get aggregated metrics for the Decision Review Layer.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReviewMetrics with current metric values.
        """
        ...


class DecisionReviewManager(ABC):
    """Internal manager interface for the Decision Review Layer.

    Lightweight facade over the DecisionReviewCoordinator for
    internal use by DecisionReviewService. Not intended for
    external consumers.
    """

    @abstractmethod
    def start_review(
        self,
        request: ReviewRequest,
        correlation_id: str = "",
    ) -> ReviewSession:
        """Start a review operation.

        Args:
            request: The review request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created review session.
        """
        ...

    @abstractmethod
    def get_decision(
        self,
        decision_id: str,
    ) -> ReviewDecision | None:
        """Retrieve a review decision by ID.

        Args:
            decision_id: The decision identifier.

        Returns:
            ReviewDecision if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_session(
        self,
        session_id: str,
    ) -> ReviewSession | None:
        """Retrieve a review session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            ReviewSession if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_health(self) -> ReviewHealth:
        """Get the health status of the Decision Review Layer.

        Returns:
            ReviewHealth with current component statuses.
        """
        ...

    @abstractmethod
    def get_metrics(self) -> ReviewMetrics:
        """Get aggregated metrics for the Decision Review Layer.

        Returns:
            ReviewMetrics with current metric values.
        """
        ...


class DecisionReviewCoordinator(ABC):
    """Coordinator interface for the review pipeline.

    Orchestrates the full review pipeline by delegating
    to sub-components in the correct order.
    """

    @abstractmethod
    def review(
        self,
        request: ReviewRequest,
        correlation_id: str = "",
    ) -> ReviewDecision:
        """Execute a full review pipeline.

        Args:
            request: The review request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The review decision.
        """
        ...

    @abstractmethod
    def get_decision(
        self,
        decision_id: str,
    ) -> ReviewDecision | None:
        """Retrieve a review decision by ID.

        Args:
            decision_id: The decision identifier.

        Returns:
            ReviewDecision if found, None otherwise.
        """
        ...

    @abstractmethod
    def health(self) -> ReviewHealth:
        """Get the health status of all sub-components.

        Returns:
            ReviewHealth with component statuses.
        """
        ...

    @abstractmethod
    def metrics(self) -> ReviewMetrics:
        """Get aggregated metrics from all sub-components.

        Returns:
            ReviewMetrics with current values.
        """
        ...


class ReviewValidator(ABC):
    """Interface for review validation.

    Validates review requests and decisions for correctness
    and consistency.
    """

    @abstractmethod
    def validate_request(
        self,
        request: ReviewRequest,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate a review request.

        Args:
            request: The review request to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...

    @abstractmethod
    def validate_decision(
        self,
        decision: ReviewDecision,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate a review decision.

        Args:
            decision: The review decision to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...


class ReviewPolicyEngine(ABC):
    """Interface for the review policy engine.

    Evaluates policies and constraints against review
    outcomes, reviewer roles, and session configurations.
    """

    @abstractmethod
    def check_policy(
        self,
        policy: ReviewPolicy,
        outcome: ReviewOutcome,
        reviewer_role: ReviewerRole,
        correlation_id: str = "",
    ) -> list[str]:
        """Check policy compliance for a review outcome.

        Args:
            policy: The review policy to check.
            outcome: The review outcome to evaluate.
            reviewer_role: The role of the reviewer.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of policy violations (empty if compliant).
        """
        ...

    @abstractmethod
    def get_policy(
        self,
        policy_id: str,
    ) -> ReviewPolicy | None:
        """Retrieve a review policy by ID.

        Args:
            policy_id: The policy identifier.

        Returns:
            ReviewPolicy if found, None otherwise.
        """
        ...


class EscalationManager(ABC):
    """Interface for escalation management.

    Manages escalation of review sessions based on
    rules, triggers, and target roles.
    """

    @abstractmethod
    def escalate(
        self,
        session_id: str,
        reason: str,
        correlation_id: str = "",
    ) -> bool:
        """Escalate a review session.

        Args:
            session_id: The session identifier to escalate.
            reason: The reason for escalation.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if escalation was successful, False otherwise.
        """
        ...

    @abstractmethod
    def get_escalation_rule(
        self,
        rule_id: str,
    ) -> EscalationRule | None:
        """Retrieve an escalation rule by ID.

        Args:
            rule_id: The rule identifier.

        Returns:
            EscalationRule if found, None otherwise.
        """
        ...


class ApprovalWorkflowManager(ABC):
    """Interface for approval workflow management.

    Manages approval workflows including starting,
    tracking, and completing multi-step approval processes.
    """

    @abstractmethod
    def start_workflow(
        self,
        session_id: str,
        workflow_type: ApprovalWorkflowType,
        correlation_id: str = "",
    ) -> bool:
        """Start an approval workflow for a review session.

        Args:
            session_id: The session identifier to start a workflow for.
            workflow_type: The type of approval workflow.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if the workflow was started successfully, False otherwise.
        """
        ...

    @abstractmethod
    def get_workflow(
        self,
        workflow_id: str,
    ) -> ApprovalWorkflow | None:
        """Retrieve an approval workflow by ID.

        Args:
            workflow_id: The workflow identifier.

        Returns:
            ApprovalWorkflow if found, None otherwise.
        """
        ...


class ReviewAuditManager(ABC):
    """Interface for review audit management.

    Records and retrieves audit trail entries for
    review operations, decisions, and status transitions.
    """

    @abstractmethod
    def record_action(
        self,
        decision_id: str,
        reviewer_id: str,
        action: str,
        previous_status: ReviewStatus | None,
        new_status: ReviewStatus | None,
        correlation_id: str = "",
    ) -> ReviewAudit:
        """Record an audit action for a review decision.

        Args:
            decision_id: The decision identifier.
            reviewer_id: The reviewer who performed the action.
            action: The action performed.
            previous_status: Previous status before the action.
            new_status: New status after the action.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created ReviewAudit entry.
        """
        ...

    @abstractmethod
    def get_audit_trail(
        self,
        decision_id: str,
    ) -> list[ReviewAudit]:
        """Get the audit trail for a review decision.

        Args:
            decision_id: The decision identifier.

        Returns:
            List of ReviewAudit entries for the decision.
        """
        ...
