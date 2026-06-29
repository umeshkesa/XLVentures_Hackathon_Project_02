"""TimelineBuilder — builds explanation timelines.

Deterministic placeholder that creates chronological timelines
of explanation events from requests, narratives, and citations.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.explainability.contracts.models import (
    ExplanationCitation,
    ExplanationNarrative,
    ExplanationRequest,
)
from adip.explainability.execution.models import ExplanationTimeline

log = structlog.get_logger(__name__)


class TimelineBuilder:
    """Builds chronological timelines for explanations.

    Deterministic placeholder that creates ExplanationTimeline
    instances with events for request, narrative creation, and
    citation building stages.
    """

    def build(
        self,
        request: ExplanationRequest,
        narratives: list[ExplanationNarrative],
        citations: list[ExplanationCitation],
        correlation_id: str = "",
    ) -> ExplanationTimeline:
        """Build a timeline for an explanation operation.

        Creates a chronological timeline with events for the
        request, narrative creation, and citation building stages.

        Args:
            request: The explanation request.
            narratives: The narratives generated for this explanation.
            citations: The citations generated for this explanation.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            An ExplanationTimeline with chronological events.
        """
        now = datetime.now(UTC)
        start_time = request.created_at

        events: list[dict[str, Any]] = [
            {
                "event_type": "request_created",
                "description": f"Explanation request created for domain {request.domain.value}",
                "timestamp": start_time.isoformat(),
                "metadata": {"request_id": str(request.request_id), "correlation_id": correlation_id},
            },
        ]

        for i, narrative in enumerate(narratives):
            events.append({
                "event_type": "narrative_created",
                "description": f"Narrative {i + 1} created for audience {narrative.audience.value}",
                "timestamp": narrative.created_at.isoformat(),
                "metadata": {"narrative_id": str(narrative.narrative_id), "audience": narrative.audience.value},
            })

        for i, citation in enumerate(citations):
            events.append({
                "event_type": "citation_created",
                "description": f"Citation {i + 1} created of type {citation.citation_type.value}",
                "timestamp": citation.created_at.isoformat(),
                "metadata": {"citation_id": str(citation.citation_id), "citation_type": citation.citation_type.value},
            })

        total_duration_ms = (now - start_time).total_seconds() * 1000

        timeline = ExplanationTimeline(
            explanation_id=str(request.request_id),
            events=events,
            start_time=start_time,
            end_time=now,
            total_duration_ms=round(total_duration_ms, 2),
            metadata={
                "correlation_id": correlation_id,
                "narrative_count": len(narratives),
                "citation_count": len(citations),
            },
        )
        log.info(
            "Timeline built",
            explanation_id=timeline.explanation_id,
            events=len(events),
            total_duration_ms=timeline.total_duration_ms,
        )
        return timeline
