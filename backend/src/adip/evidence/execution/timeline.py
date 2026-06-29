"""Evidence timeline construction.

Builds chronological timelines of evidence events.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from adip.evidence.contracts.models import Evidence
from adip.evidence.execution.models import Timeline, TimelineEntry


class EvidenceTimelineManager:
    """Manages chronological timelines of evidence events.

    Deterministic placeholder that creates timelines from evidence.
    """

    def build_timeline(self, evidence_list: list[Evidence]) -> Timeline:
        """Build a chronological timeline from evidence.

        Args:
            evidence_list: List of evidence to include.

        Returns:
            A Timeline with entries sorted chronologically.
        """
        entries: list[TimelineEntry] = []
        for ev in evidence_list:
            entry = TimelineEntry(
                entry_id=str(uuid.uuid4()),
                evidence_id=ev.evidence_id,
                event_time=ev.timestamp,
                collection_time=ev.timestamp,
                processing_time=None,
                version_time=None,
                evidence_type=ev.evidence_type,
                domain=ev.domain,
                label=f"Evidence collected from {ev.source.source_id}",
                metadata={
                    "source_type": ev.evidence_type.value if ev.evidence_type else "",
                    "domain": ev.domain.value if ev.domain else "",
                    "status": ev.status.value if ev.status else "",
                    "source_id": ev.source.source_id,
                },
            )
            entries.append(entry)

        entries.sort(key=lambda e: e.event_time)

        return Timeline(
            timeline_id=str(uuid.uuid4()),
            entries=entries,
            created_at=datetime.now(UTC),
        )

    def get_by_time_range(
        self,
        timeline: Timeline,
        start: datetime,
        end: datetime,
    ) -> list[TimelineEntry]:
        """Get timeline entries within a time range.

        Args:
            timeline: The timeline to filter.
            start: Start of the time range.
            end: End of the time range.

        Returns:
            List of TimelineEntry within the range.
        """
        return [
            entry
            for entry in timeline.entries
            if start <= entry.event_time <= end
        ]
