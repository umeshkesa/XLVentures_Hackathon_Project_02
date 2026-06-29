"""ReviewSessionManager — manages review session lifecycle.

Tracks session lifecycle, stores session data, and provides
session statistics. Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.review.contracts.models import ReviewSession
from adip.review.enums import ReviewDomain, ReviewStatus

log = structlog.get_logger(__name__)

_VALID_TRANSITIONS: dict[ReviewStatus, set[ReviewStatus]] = {
    ReviewStatus.INITIALIZED: {ReviewStatus.UNDER_REVIEW, ReviewStatus.COMPLETED, ReviewStatus.ESCALATED},
    ReviewStatus.UNDER_REVIEW: {ReviewStatus.PENDING_APPROVAL, ReviewStatus.ESCALATED, ReviewStatus.COMPLETED},
    ReviewStatus.PENDING_APPROVAL: {ReviewStatus.APPROVED, ReviewStatus.REJECTED, ReviewStatus.ESCALATED, ReviewStatus.COMPLETED},
    ReviewStatus.APPROVED: {ReviewStatus.COMPLETED},
    ReviewStatus.REJECTED: {ReviewStatus.COMPLETED},
    ReviewStatus.ESCALATED: {ReviewStatus.UNDER_REVIEW, ReviewStatus.COMPLETED},
    ReviewStatus.COMPLETED: set(),
}


class ReviewSessionManager:
    """Manages review session lifecycle.

    Deterministic placeholder that creates, tracks, and manages
    sessions for review operations.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ReviewSession] = {}

    def create_session(
        self,
        request_id: str,
        reviewer_id: str = "",
        role: str = "",
        domain: str = "SYSTEM",
        correlation_id: str = "",
    ) -> ReviewSession:
        """Create a new review session.

        Args:
            request_id: The request identifier.
            reviewer_id: Optional reviewer identifier.
            role: Optional reviewer role.
            domain: Optional review domain.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created ReviewSession with INITIALIZED status.
        """
        from adip.review.enums import ReviewerRole as ReviewerRoleEnum

        role_enum = ReviewerRoleEnum.ENGINEER
        try:
            if role:
                role_enum = ReviewerRoleEnum(role)
        except ValueError:
            role_enum = ReviewerRoleEnum.ENGINEER

        domain_enum = ReviewDomain.SYSTEM
        try:
            if domain:
                domain_enum = ReviewDomain(domain)
        except ValueError:
            domain_enum = ReviewDomain.SYSTEM

        session = ReviewSession(
            request_id=uuid.UUID(request_id) if isinstance(request_id, str) else request_id,
            reviewer_id=reviewer_id,
            role=role_enum,
            status=ReviewStatus.INITIALIZED,
            started_at=datetime.now(UTC),
            completed_at=None,
            metadata={"correlation_id": correlation_id, "domain": domain},
        )
        sid = str(session.session_id)
        self._sessions[sid] = session
        log.info("session.created", session_id=sid, correlation_id=correlation_id)
        return session

    def get_session(self, session_id: str) -> ReviewSession | None:
        """Get a session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            ReviewSession if found, None otherwise.
        """
        return self._sessions.get(session_id)

    def update_status(self, session_id: str, status: ReviewStatus) -> ReviewSession | None:
        """Update the status of a session with transition validation.

        Validates transitions:
        INITIALIZED → UNDER_REVIEW → PENDING_APPROVAL → APPROVED/REJECTED
        Any state → COMPLETED/ESCALATED (where valid).

        Args:
            session_id: The session identifier.
            status: The new status.

        Returns:
            Updated session if found and transition valid, None otherwise.
        """
        session = self._sessions.get(session_id)
        if session is None:
            return None

        allowed = _VALID_TRANSITIONS.get(session.status, set())
        if status not in allowed:
            log.warning(
                "session.invalid_transition",
                session_id=session_id,
                current=session.status.value,
                requested=status.value,
                allowed=[s.value for s in allowed],
            )
            return None

        session.status = status
        if status == ReviewStatus.COMPLETED:
            session.completed_at = datetime.now(UTC)
        self._sessions[session_id] = session
        log.info("session.status_updated", session_id=session_id, status=status.value)
        return session

    def get_active_sessions(self) -> list[ReviewSession]:
        """Get all active (non-terminal) sessions.

        Returns:
            List of active ReviewSession instances.
        """
        terminal = {ReviewStatus.COMPLETED}
        return [s for s in self._sessions.values() if s.status not in terminal]

    def get_all_sessions(self) -> list[ReviewSession]:
        """Get all sessions.

        Returns:
            List of all ReviewSession instances.
        """
        return list(self._sessions.values())

    def clear(self) -> None:
        """Clear all sessions."""
        self._sessions.clear()
        log.info("sessions.cleared")

    def count(self) -> int:
        """Get the number of sessions.

        Returns:
            The number of sessions.
        """
        return len(self._sessions)
