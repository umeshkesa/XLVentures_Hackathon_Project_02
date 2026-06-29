"""ReasoningSessionManager — manages reasoning session lifecycle.

Creates, tracks, and completes reasoning sessions with timing,
hypothesis/inference/contradiction tracking, correlation support,
risk tracking, and impact tracking.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.reasoning.contracts.models import ReasoningDomain, ReasoningSession, ReasoningStatus
from adip.reasoning.enums import ReasoningStrategyType
from adip.reasoning.execution.models import ImpactAssessment, RiskAssessment

log = structlog.get_logger(__name__)


class ReasoningSessionManager:
    """Manages reasoning session lifecycle."""

    def __init__(self) -> None:
        self._sessions: dict[str, ReasoningSession] = {}

    def create_session(
        self,
        request_id: str,
        domain: ReasoningDomain = ReasoningDomain.SYSTEM,
        user_id: str = "",
        correlation_id: str = "",
        strategy_type: ReasoningStrategyType = ReasoningStrategyType.HYBRID,
        goal_type: str = "",
        strategy: str = "",
        constraints_count: int = 0,
        assumptions_count: int = 0,
    ) -> ReasoningSession:
        """Create a new reasoning session.

        Args:
            request_id: The reasoning request ID.
            domain: The reasoning domain.
            user_id: User identifier.
            correlation_id: Correlation ID for tracing.
            strategy_type: The reasoning strategy type.
            goal_type: The type of reasoning goal.
            strategy: The strategy name.
            constraints_count: Number of constraints.
            assumptions_count: Number of assumptions.

        Returns:
            The created ReasoningSession.
        """
        session = ReasoningSession(
            request_id=uuid.UUID(request_id),
            domain=domain,
            status=ReasoningStatus.INITIALIZED,
            metadata={
                "user_id": user_id,
                "correlation_id": correlation_id or str(uuid.uuid4()),
                "strategy_type": strategy_type.value,
                "hypotheses_count": 0,
                "inferences_count": 0,
                "contradictions_count": 0,
                "decisions_count": 0,
                "goal_type": goal_type,
                "strategy": strategy,
                "constraints_count": constraints_count,
                "assumptions_count": assumptions_count,
            },
        )
        self._sessions[str(session.session_id)] = session
        log.info(
            "session_manager.create_session",
            session_id=str(session.session_id),
            domain=domain.value,
            correlation_id=correlation_id,
        )
        return session

    def get_session(self, session_id: str) -> ReasoningSession | None:
        """Retrieve a session by ID."""
        return self._sessions.get(session_id)

    def complete_session(self, session_id: str) -> ReasoningSession | None:
        """Mark a session as completed with timing."""
        session = self._sessions.get(session_id)
        if session is None:
            return None

        now = datetime.now(UTC)
        duration = (now - session.started_at).total_seconds() * 1000
        session.completed_at = now
        session.status = ReasoningStatus.COMPLETED
        session.statistics["duration_ms"] = round(duration, 2)
        log.info(
            "session_manager.complete_session",
            session_id=session_id,
            duration_ms=round(duration, 2),
        )
        return session

    def update_session_metadata(
        self,
        session_id: str,
        key: str,
        value: object,
    ) -> bool:
        """Update a metadata field on the session."""
        session = self._sessions.get(session_id)
        if session is None:
            return False
        session.metadata[key] = value
        return True

    def track_risk(
        self,
        session_id: str,
        risk: RiskAssessment,
    ) -> bool:
        """Track a risk assessment on a session.

        Args:
            session_id: The session ID.
            risk: The RiskAssessment to track.

        Returns:
            True if tracked, False if session not found.
        """
        session = self._sessions.get(session_id)
        if session is None:
            return False
        risks = session.statistics.setdefault("risks", [])
        risks.append({
            "risk_id": risk.risk_id,
            "risk_type": risk.risk_type,
            "score": risk.score,
            "level": risk.level,
        })
        return True

    def track_impact(
        self,
        session_id: str,
        impact: ImpactAssessment,
    ) -> bool:
        """Track an impact assessment on a session.

        Args:
            session_id: The session ID.
            impact: The ImpactAssessment to track.

        Returns:
            True if tracked, False if session not found.
        """
        session = self._sessions.get(session_id)
        if session is None:
            return False
        impacts = session.statistics.setdefault("impacts", [])
        impacts.append({
            "impact_id": impact.impact_id,
            "impact_type": impact.impact_type,
            "score": impact.score,
        })
        return True

    def get_active_sessions(self) -> list[ReasoningSession]:
        """Return all sessions that have not completed."""
        return [s for s in self._sessions.values() if s.completed_at is None]

    def clear(self) -> None:
        """Clear all sessions."""
        self._sessions.clear()
