"""ExplanationSnapshot — creates immutable explanation snapshots.

Captures point-in-time snapshots of packages, narratives,
citations, trace, and timelines. Deterministic placeholder.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

log = structlog.get_logger(__name__)


class ExplanationSnapshot:
    """Creates immutable snapshots of explanation state.

    Deterministic placeholder that captures point-in-time state
    of packages, narratives, citations, trace, and timelines.
    """

    def __init__(self) -> None:
        self._snapshots: list[dict[str, Any]] = []
        self._snapshots_by_id: dict[str, dict[str, Any]] = {}

    def create(
        self,
        package: Any,
        narratives: list[Any],
        citations: list[Any],
        trace: list[Any],
        timeline: Any,
        correlation_id: str = "",
        confidence: Any = None,
        quality: Any = None,
        compliance: Any = None,
        version: str = "",
    ) -> dict[str, Any]:
        """Create an immutable snapshot.

        Args:
            package: The explanation package to snapshot.
            narratives: List of narratives to include.
            citations: List of citations to include.
            trace: List of trace records to include.
            timeline: The timeline to include.
            correlation_id: Optional correlation ID for tracing.
            confidence: Optional confidence score or model.
            quality: Optional quality score or model.
            compliance: Optional compliance result or model.
            version: Optional version string.

        Returns:
            Dictionary with snapshot metadata.
        """
        explanation_id = str(getattr(package, "package_id", ""))
        snapshot = {
            "snapshot_id": str(uuid.uuid4()),
            "explanation_id": explanation_id,
            "package_id": str(getattr(package, "package_id", "")),
            "narrative_count": len(narratives) if narratives else 0,
            "citation_count": len(citations) if citations else 0,
            "trace_count": len(trace) if trace else 0,
            "timeline_id": str(getattr(timeline, "timeline_id", "")),
            "timeline_event_count": len(getattr(timeline, "events", [])),
            "confidence": confidence,
            "quality": quality,
            "compliance": compliance,
            "version": version,
            "created_at": datetime.now(UTC).isoformat(),
        }
        self._snapshots.append(snapshot)
        self._snapshots_by_id[snapshot["snapshot_id"]] = snapshot
        log.info(
            "snapshot.created",
            explanation_id=explanation_id,
            snapshot_id=snapshot["snapshot_id"],
            correlation_id=correlation_id,
        )
        return snapshot

    def get(self, snapshot_id: str) -> dict[str, Any] | None:
        """Get a snapshot by ID.

        Args:
            snapshot_id: The snapshot identifier.

        Returns:
            Snapshot dictionary if found, None otherwise.
        """
        return self._snapshots_by_id.get(snapshot_id)

    def get_by_explanation(self, explanation_id: str) -> list[dict[str, Any]]:
        """Get all snapshots for an explanation.

        Args:
            explanation_id: The explanation identifier.

        Returns:
            List of snapshot dictionaries.
        """
        return [s for s in self._snapshots if s.get("explanation_id") == explanation_id]

    def clear(self) -> None:
        """Clear all snapshots."""
        self._snapshots.clear()
        self._snapshots_by_id.clear()
        log.info("snapshots.cleared")

    def count(self) -> int:
        """Get the number of snapshots.

        Returns:
            The number of snapshots.
        """
        return len(self._snapshots)
