"""ExplanationJustification — records explanation justifications.

Provides structured storage for the reasoning behind narrative,
citation, template, audience, and policy decisions. Deterministic
placeholder implementation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import structlog

log = structlog.get_logger(__name__)


class ExplanationJustification:
    """Records justifications for explanation decisions.

    Deterministic placeholder that stores why each narrative, citation,
    template, audience, and policy was selected during explanation.
    """

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    def _create_record(
        self,
        explanation_id: str,
        category: str,
        target_id: str,
        why: str,
        correlation_id: str = "",
    ) -> dict[str, Any]:
        record = {
            "id": str(uuid.uuid4()),
            "explanation_id": explanation_id,
            "category": category,
            "target_id": target_id,
            "why": why,
            "correlation_id": correlation_id,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self._records.append(record)
        log.info(
            "justification.recorded",
            category=category,
            explanation_id=explanation_id,
            correlation_id=correlation_id,
        )
        return record

    def record_narrative_justification(
        self,
        narrative_id: str = "",
        why: str = "",
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Record why a specific narrative was selected.

        Args:
            narrative_id: The narrative identifier.
            why: The reason this narrative was selected.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dictionary with justification record data.
        """
        return self._create_record("", "narrative", narrative_id, why, correlation_id)

    def record_citation_justification(
        self,
        citation_id: str = "",
        why: str = "",
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Record why a specific citation was included.

        Args:
            citation_id: The citation identifier.
            why: The reason this citation was included.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dictionary with justification record data.
        """
        return self._create_record("", "citation", citation_id, why, correlation_id)

    def record_template_justification(
        self,
        template_type: str = "",
        why: str = "",
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Record why a specific template was chosen.

        Args:
            template_type: The template type identifier.
            why: The reason this template was chosen.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dictionary with justification record data.
        """
        return self._create_record("", "template", template_type, why, correlation_id)

    def record_audience_justification(
        self,
        audience: str = "",
        why: str = "",
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Record why a specific audience was targeted.

        Args:
            audience: The audience identifier.
            why: The reason this audience was targeted.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dictionary with justification record data.
        """
        return self._create_record("", "audience", audience, why, correlation_id)

    def record_policy_justification(
        self,
        policy_type: str = "",
        why: str = "",
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Record why a specific policy was applied.

        Args:
            policy_type: The policy type identifier.
            why: The reason this policy was applied.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dictionary with justification record data.
        """
        return self._create_record("", "policy", policy_type, why, correlation_id)

    def get_justifications(self, explanation_id: str) -> list[dict[str, Any]]:
        """Get all justifications for an explanation.

        Args:
            explanation_id: The explanation identifier.

        Returns:
            List of justification record dictionaries.
        """
        return [r for r in self._records if r["explanation_id"] == explanation_id]

    def get_by_category(self, explanation_id: str, category: str) -> list[dict[str, Any]]:
        """Get justifications for an explanation filtered by category.

        Args:
            explanation_id: The explanation identifier.
            category: The category to filter by (narrative, citation,
                template, audience, policy).

        Returns:
            List of justification record dictionaries matching the category.
        """
        return [
            r
            for r in self._records
            if r["explanation_id"] == explanation_id and r["category"] == category
        ]

    def get_all(self) -> list[dict[str, Any]]:
        """Get all justification records.

        Returns:
            List of all justification record dictionaries.
        """
        return list(self._records)

    def clear(self) -> None:
        """Clear all justification records."""
        self._records.clear()
        log.info("justifications.cleared")

    def count(self) -> int:
        """Get the number of justification records.

        Returns:
            The number of justification records.
        """
        return len(self._records)
