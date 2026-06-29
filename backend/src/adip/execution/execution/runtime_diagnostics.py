"""RuntimeDiagnostics — collects runtime diagnostic information.

Deterministic placeholder that tracks and categorises execution
failures: task failures, dependency failures, scheduler failures,
policy violations, and resource failures. Phase 3.5.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog
from pydantic import UUID4, BaseModel, Field

log = structlog.get_logger(__name__)


class DiagnosticEvent(BaseModel):
    """A single diagnostic event during execution."""

    event_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique diagnostic event identifier",
    )
    session_id: str = Field(
        default="",
        description="The session this event belongs to",
    )
    category: str = Field(
        default="",
        description="Category: task, dependency, scheduler, policy, resource",
    )
    severity: str = Field(
        default="WARNING",
        description="Severity: INFO, WARNING, ERROR, CRITICAL",
    )
    message: str = Field(
        default="",
        description="Diagnostic message",
    )
    details: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional diagnostic details",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the event occurred",
    )


class DiagnosticsSummary(BaseModel):
    """Summary of all diagnostics for a session."""

    summary_id: UUID4 = Field(
        default_factory=uuid.uuid4,
        description="Unique summary identifier",
    )
    session_id: str = Field(
        default="",
        description="The session this summary belongs to",
    )
    total_events: int = Field(
        default=0,
        ge=0,
        description="Total number of diagnostic events",
    )
    task_failures: int = Field(
        default=0,
        ge=0,
        description="Number of task failures",
    )
    dependency_failures: int = Field(
        default=0,
        ge=0,
        description="Number of dependency failures",
    )
    scheduler_failures: int = Field(
        default=0,
        ge=0,
        description="Number of scheduler failures",
    )
    policy_violations: int = Field(
        default=0,
        ge=0,
        description="Number of policy violations",
    )
    resource_failures: int = Field(
        default=0,
        ge=0,
        description="Number of resource failures",
    )
    events: list[DiagnosticEvent] = Field(
        default_factory=list,
        description="Diagnostic events included in this summary",
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="When the summary was generated",
    )


class RuntimeDiagnostics:
    """Collects and categorises runtime diagnostic events.

    Tracks failures across 5 categories:
    - Task failures: individual task execution errors
    - Dependency failures: dependency resolution errors
    - Scheduler failures: scheduling or timing errors
    - Policy violations: policy compliance failures
    - Resource failures: resource availability errors
    """

    def __init__(self) -> None:
        self._events: list[DiagnosticEvent] = []

    def record_event(
        self,
        session_id: str,
        category: str,
        severity: str = "WARNING",
        message: str = "",
        details: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> DiagnosticEvent:
        """Record a diagnostic event.

        Args:
            session_id: The session ID.
            category: Event category.
            severity: Event severity.
            message: Diagnostic message.
            details: Additional details.
            correlation_id: Optional correlation ID.

        Returns:
            The created DiagnosticEvent.
        """
        event = DiagnosticEvent(
            session_id=session_id,
            category=category,
            severity=severity,
            message=message,
            details=details or {},
        )
        self._events.append(event)
        log.info(
            "diagnostics.event",
            session_id=session_id,
            category=category,
            severity=severity,
            cid=correlation_id,
        )
        return event

    def get_summary(self, session_id: str) -> DiagnosticsSummary:
        """Get a diagnostic summary for a session.

        Args:
            session_id: The session identifier.

        Returns:
            DiagnosticsSummary with categorised counts.
        """
        session_events = [e for e in self._events if e.session_id == session_id]
        return DiagnosticsSummary(
            session_id=session_id,
            total_events=len(session_events),
            task_failures=sum(1 for e in session_events if e.category == "task"),
            dependency_failures=sum(1 for e in session_events if e.category == "dependency"),
            scheduler_failures=sum(1 for e in session_events if e.category == "scheduler"),
            policy_violations=sum(1 for e in session_events if e.category == "policy"),
            resource_failures=sum(1 for e in session_events if e.category == "resource"),
            events=session_events,
        )

    def get_all_events(self) -> list[DiagnosticEvent]:
        """Get all diagnostic events.

        Returns:
            List of DiagnosticEvent objects.
        """
        return list(self._events)

    def get_events_by_category(self, category: str) -> list[DiagnosticEvent]:
        """Get events filtered by category.

        Args:
            category: The category to filter by.

        Returns:
            List of DiagnosticEvent objects.
        """
        return [e for e in self._events if e.category == category]

    def get_event_count(self) -> int:
        """Get total event count.

        Returns:
            Total event count.
        """
        return len(self._events)

    def clear(self) -> None:
        """Clear all diagnostic events."""
        self._events.clear()
