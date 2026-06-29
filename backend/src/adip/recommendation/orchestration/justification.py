"""RecommendationJustification — records recommendation justifications.

Provides structured storage for the reasoning, evidence, business
goals, constraints, and policies that support each recommendation.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

log = structlog.get_logger(__name__)


class JustificationRecord:
    """A justification record for a recommendation.

    Attributes:
        justification_id: Unique justification identifier.
        recommendation_id: The recommendation this justification supports.
        supporting_reasoning: The reasoning behind the recommendation.
        supporting_evidence: Evidence supporting the recommendation.
        business_goals: Business goals addressed.
        constraints: Constraints considered.
        policies: Policies applied.
        tradeoffs: Tradeoffs considered.
        created_at: When the justification was created.
    """

    def __init__(
        self,
        justification_id: str = "",
        recommendation_id: str = "",
        supporting_reasoning: str = "",
        supporting_evidence: list[str] | None = None,
        business_goals: list[str] | None = None,
        constraints: list[str] | None = None,
        policies: list[str] | None = None,
        tradeoffs: list[str] | None = None,
        created_at: datetime | None = None,
    ) -> None:
        self.justification_id = justification_id or str(uuid.uuid4())
        self.recommendation_id = recommendation_id
        self.supporting_reasoning = supporting_reasoning
        self.supporting_evidence = supporting_evidence or []
        self.business_goals = business_goals or []
        self.constraints = constraints or []
        self.policies = policies or []
        self.tradeoffs = tradeoffs or []
        self.created_at = created_at or datetime.now(UTC)


class RecommendationJustification:
    """Records justifications for recommendation decisions.

    Deterministic placeholder that stores structured justification
    records with reasoning, evidence, goals, constraints, and policies.
    """

    def __init__(self) -> None:
        self._records: list[JustificationRecord] = []

    def record(
        self,
        recommendation_id: str = "",
        supporting_reasoning: str = "",
        supporting_evidence: list[str] | None = None,
        business_goals: list[str] | None = None,
        constraints: list[str] | None = None,
        policies: list[str] | None = None,
        tradeoffs: list[str] | None = None,
    ) -> JustificationRecord:
        """Record a justification for a recommendation.

        Args:
            recommendation_id: The recommendation identifier.
            supporting_reasoning: The reasoning behind the recommendation.
            supporting_evidence: Evidence supporting the recommendation.
            business_goals: Business goals addressed.
            constraints: Constraints considered.
            policies: Policies applied.
            tradeoffs: Tradeoffs considered.

        Returns:
            The created JustificationRecord.
        """
        record = JustificationRecord(
            recommendation_id=recommendation_id,
            supporting_reasoning=supporting_reasoning,
            supporting_evidence=supporting_evidence or [],
            business_goals=business_goals or [],
            constraints=constraints or [],
            policies=policies or [],
            tradeoffs=tradeoffs or [],
        )
        self._records.append(record)
        log.info("justification.recorded", recommendation_id=recommendation_id)
        return record

    def get_by_recommendation(self, recommendation_id: str) -> list[JustificationRecord]:
        """Get all justifications for a recommendation.

        Args:
            recommendation_id: The recommendation identifier.

        Returns:
            List of JustificationRecord.
        """
        return [r for r in self._records if r.recommendation_id == recommendation_id]

    def get_all(self) -> list[JustificationRecord]:
        """Get all justification records."""
        return list(self._records)

    def clear(self) -> None:
        """Clear all justification records."""
        self._records.clear()

    def count(self) -> int:
        """Get the number of justification records."""
        return len(self._records)
