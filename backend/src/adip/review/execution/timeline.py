"""ReviewTimeline — chronological event tracking for review operations.

Records and queries timeline events for review lifecycle
including submission, assignment, start, modification,
approval, rejection, and escalation events.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.review.execution.models import TimelineEvent

log = structlog.get_logger(__name__)


class ReviewTimeline:
    """In-memory timeline manager for review events."""

    def __init__(self) -> None:
        self._events: list[TimelineEvent] = []

    def _create_event(
        self,
        review_id: str,
        event_type: str,
        performed_by: str = "",
        description: str = "",
        correlation_id: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> TimelineEvent:
        event = TimelineEvent(
            review_id=review_id,
            event_type=event_type,
            performed_by=performed_by,
            description=description,
            timestamp=datetime.now(UTC),
            metadata={
                **(metadata or {}),
                "correlation_id": correlation_id,
            },
        )
        log.info(
            "review_timeline.event",
            review_id=review_id,
            event_type=event_type,
            performed_by=performed_by,
            correlation_id=correlation_id,
        )
        self._events.append(event)
        return event

    def record_submitted(
        self,
        review_id: str,
        performed_by: str = "",
        description: str = "",
        correlation_id: str = "",
    ) -> TimelineEvent:
        """Record a submission event."""
        return self._create_event(
            review_id=review_id,
            event_type="submitted",
            performed_by=performed_by,
            description=description or "Review submitted",
            correlation_id=correlation_id,
        )

    def record_assigned(
        self,
        review_id: str,
        performed_by: str = "",
        description: str = "",
        correlation_id: str = "",
    ) -> TimelineEvent:
        """Record an assignment event."""
        return self._create_event(
            review_id=review_id,
            event_type="assigned",
            performed_by=performed_by,
            description=description or "Reviewer assigned",
            correlation_id=correlation_id,
        )

    def record_started(
        self,
        review_id: str,
        performed_by: str = "",
        description: str = "",
        correlation_id: str = "",
    ) -> TimelineEvent:
        """Record a started event."""
        return self._create_event(
            review_id=review_id,
            event_type="started",
            performed_by=performed_by,
            description=description or "Review started",
            correlation_id=correlation_id,
        )

    def record_modified(
        self,
        review_id: str,
        performed_by: str = "",
        description: str = "",
        correlation_id: str = "",
    ) -> TimelineEvent:
        """Record a modification event."""
        return self._create_event(
            review_id=review_id,
            event_type="modified",
            performed_by=performed_by,
            description=description or "Review modified",
            correlation_id=correlation_id,
        )

    def record_approved(
        self,
        review_id: str,
        performed_by: str = "",
        description: str = "",
        correlation_id: str = "",
    ) -> TimelineEvent:
        """Record an approval event."""
        return self._create_event(
            review_id=review_id,
            event_type="approved",
            performed_by=performed_by,
            description=description or "Review approved",
            correlation_id=correlation_id,
        )

    def record_rejected(
        self,
        review_id: str,
        performed_by: str = "",
        description: str = "",
        correlation_id: str = "",
    ) -> TimelineEvent:
        """Record a rejection event."""
        return self._create_event(
            review_id=review_id,
            event_type="rejected",
            performed_by=performed_by,
            description=description or "Review rejected",
            correlation_id=correlation_id,
        )

    def record_escalated(
        self,
        review_id: str,
        performed_by: str = "",
        description: str = "",
        correlation_id: str = "",
    ) -> TimelineEvent:
        """Record an escalation event."""
        return self._create_event(
            review_id=review_id,
            event_type="escalated",
            performed_by=performed_by,
            description=description or "Review escalated",
            correlation_id=correlation_id,
        )

    def record_event(
        self,
        review_id: str,
        event_type: str,
        performed_by: str = "",
        description: str = "",
        correlation_id: str = "",
    ) -> TimelineEvent:
        """Record a generic timeline event."""
        return self._create_event(
            review_id=review_id,
            event_type=event_type,
            performed_by=performed_by,
            description=description,
            correlation_id=correlation_id,
        )

    def get_timeline(self, review_id: str) -> list[TimelineEvent]:
        """Get all events for a review, sorted chronologically."""
        return sorted(
            [e for e in self._events if e.review_id == review_id],
            key=lambda e: e.timestamp,
        )

    def get_events_by_type(self, review_id: str, event_type: str) -> list[TimelineEvent]:
        """Get events for a review filtered by type."""
        return [
            e
            for e in self._events
            if e.review_id == review_id and e.event_type == event_type
        ]

    def get_all_events(self) -> list[TimelineEvent]:
        """Get all timeline events."""
        return list(self._events)

    def clear(self) -> None:
        """Clear all timeline events."""
        count = len(self._events)
        self._events.clear()
        log.info("review_timeline.clear", cleared=count)
