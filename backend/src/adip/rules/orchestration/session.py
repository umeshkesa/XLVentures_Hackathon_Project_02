"""RuleSessionManager — manages evaluation session lifecycle.

Creates, tracks, and completes evaluation sessions with timing,
rule tracking, and correlation support.
"""

from __future__ import annotations

import uuid

import structlog

from adip.rules.contracts.models import RuleDomain, RuleSession
from adip.rules.enums import EvaluationStrategyType

log = structlog.get_logger(__name__)


class RuleSessionManager:
    """Manages rule evaluation session lifecycle."""

    def __init__(self) -> None:
        self._sessions: dict[str, RuleSession] = {}

    def create_session(
        self,
        domain: RuleDomain = RuleDomain.SYSTEM,
        user_id: str = "",
        correlation_id: str = "",
        evaluation_strategy: EvaluationStrategyType = EvaluationStrategyType.SEQUENTIAL,
    ) -> RuleSession:
        """Create a new evaluation session."""
        session = RuleSession(
            domain=domain,
            user_id=user_id,
            correlation_id=correlation_id or str(uuid.uuid4()),
            evaluation_strategy=evaluation_strategy,
        )
        self._sessions[str(session.session_id)] = session
        log.info("rule_session_manager.create_session", session_id=str(session.session_id), domain=domain.value)
        return session

    def get_session(self, session_id: str) -> RuleSession | None:
        """Retrieve a session by ID."""
        return self._sessions.get(session_id)

    def complete_session(self, session_id: str) -> RuleSession | None:
        """Mark a session as completed with timing."""
        session = self._sessions.get(session_id)
        if session is None:
            return None

        from datetime import UTC, datetime

        now = datetime.now(UTC)
        duration = (now - session.started_at).total_seconds() * 1000
        session.completed_at = now
        session.duration_ms = round(duration, 2)
        log.info("rule_session_manager.complete_session", session_id=session_id, duration_ms=duration)
        return session

    def add_evaluated_rule(self, session_id: str, rule_id: str) -> bool:
        """Record a rule as evaluated in the session."""
        session = self._sessions.get(session_id)
        if session is None:
            return False
        if rule_id not in session.rules_evaluated:
            session.rules_evaluated.append(rule_id)
        return True

    def add_decision(self, session_id: str, decision) -> bool:
        """Record a decision in the session."""
        session = self._sessions.get(session_id)
        if session is None:
            return False
        session.decisions_made.append(decision)
        return True

    def get_active_sessions(self) -> list[RuleSession]:
        """Return all sessions that have not completed."""
        return [s for s in self._sessions.values() if s.completed_at is None]

    def clear(self) -> None:
        """Clear all sessions."""
        self._sessions.clear()
