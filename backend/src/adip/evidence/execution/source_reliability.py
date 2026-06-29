"""Source reliability tracking.

Maintains reliability scores for evidence sources.
"""

from __future__ import annotations

from adip.evidence.execution.models import SourceReliability


class EvidenceSourceReliability:
    """Tracks and manages source reliability scores.

    Deterministic placeholder that maintains in-memory reliability
    scores per source ID using exponential moving average.
    """

    def __init__(self) -> None:
        self._scores: dict[str, SourceReliability] = {}
        self._observations: dict[str, list[bool]] = {}

    def record_observation(
        self,
        source_id: str,
        is_valid: bool,
        source_type: str = "unknown",
    ) -> None:
        """Record a validation observation for a source.

        Updates the source's reliability score using exponential
        moving average.

        Args:
            source_id: The source ID.
            is_valid: Whether the evidence from this source was valid.
            source_type: Optional type descriptor for the source.
        """
        if source_id not in self._observations:
            self._observations[source_id] = []
        self._observations[source_id].append(is_valid)

        valid_count = sum(1 for v in self._observations[source_id] if v)
        total = len(self._observations[source_id])
        validation_rate = valid_count / max(total, 1)

        current = self._scores.get(source_id)
        alpha = 0.3
        current_reliability = current.reliability_score if current else 0.5
        new_reliability = (1 - alpha) * current_reliability + alpha * (1.0 if is_valid else 0.0)
        self._scores[source_id] = SourceReliability(
            source_id=source_id,
            source_type=source_type,
            reliability_score=new_reliability,
            historical_accuracy=validation_rate,
            validation_success_rate=validation_rate,
            ranking=0,
        )

        self._update_rankings()

    def _update_rankings(self) -> None:
        """Update source rankings based on reliability scores."""
        sorted_sources = sorted(
            self._scores.items(),
            key=lambda x: x[1].reliability_score,
            reverse=True,
        )
        for rank, (source_id, _) in enumerate(sorted_sources):
            self._scores[source_id].ranking = rank

    def get_reliability(self, source_id: str) -> float:
        """Get the reliability score for a source.

        Args:
            source_id: The source ID to query.

        Returns:
            Reliability score between 0.0 and 1.0.
        """
        source = self._scores.get(source_id)
        if source is None:
            return 0.5
        return source.reliability_score

    def get_ranking(self) -> list[SourceReliability]:
        """Get all sources sorted by reliability (highest first).

        Returns:
            List of SourceReliability sorted by score descending.
        """
        return sorted(
            self._scores.values(),
            key=lambda s: s.reliability_score,
            reverse=True,
        )

    def get_source(self, source_id: str) -> SourceReliability | None:
        """Get the full reliability record for a source.

        Args:
            source_id: The source ID to look up.

        Returns:
            SourceReliability if found, None otherwise.
        """
        return self._scores.get(source_id)

    def reset(self) -> None:
        """Clear all reliability data."""
        self._scores.clear()
        self._observations.clear()
