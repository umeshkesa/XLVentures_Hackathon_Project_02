"""TimelineManager — estimates implementation timelines.

Provides timeline estimates for recommendations based on
urgency, complexity, and constraints.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.recommendation.enums import ImplementationTimeline
from adip.recommendation.execution.models import TimelineEstimate

log = structlog.get_logger(__name__)


class TimelineManager:
    """Estimates implementation timelines for recommendations.

    Deterministic placeholder that determines timelines based on
    urgency, complexity, and operational constraints.
    """

    def estimate(
        self,
        urgency_score: float = 0.5,
        complexity: str = "medium",
        has_time_constraint: bool = False,
        factors: list[str] | None = None,
    ) -> TimelineEstimate:
        """Estimate the implementation timeline for a recommendation.

        Args:
            urgency_score: Urgency score (0.0-1.0, higher = more urgent).
            complexity: Complexity level (low, medium, high).
            has_time_constraint: Whether a time constraint exists.
            factors: Optional list of influencing factors.

        Returns:
            TimelineEstimate with recommended timeline.
        """
        factors = factors or []
        us = max(0.0, min(1.0, urgency_score))

        if us >= 0.9:
            timeline = ImplementationTimeline.IMMEDIATE
            hours = 1.0
        elif us >= 0.7:
            timeline = ImplementationTimeline.TODAY
            hours = 8.0
        elif us >= 0.5:
            timeline = ImplementationTimeline.WITHIN_24_HOURS
            hours = 24.0
        elif us >= 0.3:
            timeline = ImplementationTimeline.MAINTENANCE_WINDOW
            hours = 72.0
        else:
            timeline = ImplementationTimeline.PLANNED_FUTURE
            hours = 168.0

        if complexity == "high":
            hours *= 2
        elif complexity == "low":
            hours *= 0.5

        log.info("timeline.estimate", timeline=timeline.value, hours=hours)
        return TimelineEstimate(
            timeline=timeline,
            description=f"Implement {timeline.value.lower().replace('_', ' ')}",
            estimated_hours=round(hours, 1),
            urgency_score=us,
            factors=factors,
        )

    def estimate_priority(
        self,
        priority: str = "MEDIUM",
    ) -> TimelineEstimate:
        """Estimate timeline based on priority level.

        Args:
            priority: Priority level (CRITICAL, HIGH, MEDIUM, LOW, OPTIONAL).

        Returns:
            TimelineEstimate.
        """
        urgency_map = {
            "CRITICAL": 0.95,
            "HIGH": 0.75,
            "MEDIUM": 0.5,
            "LOW": 0.25,
            "OPTIONAL": 0.1,
        }
        urgency = urgency_map.get(priority.upper(), 0.5)
        return self.estimate(
            urgency_score=urgency,
            factors=[f"Priority-based timeline for {priority} priority"],
        )
