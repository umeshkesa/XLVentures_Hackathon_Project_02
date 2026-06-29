"""NarrativeBuilder — builds explanation narratives.

Deterministic placeholder that creates ExplanationNarrative
instances for specified audience layers and narrative types.
"""

from __future__ import annotations

import uuid
from typing import Any

import structlog

from adip.explainability.contracts.models import ExplanationNarrative
from adip.explainability.enums import ExplanationLayer, NarrativeType

log = structlog.get_logger(__name__)


_NARRATIVE_TITLES: dict[str, str] = {
    "SUMMARY": "Executive Summary",
    "DETAILED": "Detailed Explanation",
    "TECHNICAL": "Technical Analysis",
    "BUSINESS": "Business Overview",
    "AUDIT": "Audit Report",
}

_AUDIENCE_NARRATIVE_MAP: dict[str, str] = {
    "EXECUTIVE": "SUMMARY",
    "MANAGER": "SUMMARY",
    "ENGINEER": "DETAILED",
    "OPERATOR": "DETAILED",
    "TECHNICIAN": "TECHNICAL",
    "AUDITOR": "AUDIT",
    "DEVELOPER": "TECHNICAL",
}


class NarrativeBuilder:
    """Builds explanation narratives for target audiences.

    Deterministic placeholder that creates ExplanationNarrative
    instances with predefined titles and placeholder content
    based on narrative type and audience.
    """

    def __init__(self) -> None:
        self._narratives: list[ExplanationNarrative] = []
        self._default_package_id = uuid.uuid4()

    def build_narrative(
        self,
        narrative_type: str,
        audience: str,
        context: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> ExplanationNarrative:
        """Build a single narrative for a specific audience.

        Args:
            narrative_type: The type of narrative (SUMMARY, DETAILED, etc.).
            audience: The target audience layer.
            context: Optional context for narrative building.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The built ExplanationNarrative.
        """
        title = _NARRATIVE_TITLES.get(narrative_type, "Explanation")
        content = f"Placeholder {narrative_type.lower()} explanation content for {audience.lower()} audience."
        summary = f"Placeholder summary of {narrative_type.lower()} explanation for {audience.lower()}."

        narrative = ExplanationNarrative(
            package_id=self._default_package_id,
            narrative_type=NarrativeType(narrative_type),
            audience=ExplanationLayer(audience),
            title=title,
            content=content,
            summary=summary,
            metadata={"correlation_id": correlation_id, "context": context or {}},
        )
        self._narratives.append(narrative)
        log.info("Narrative built", narrative_id=str(narrative.narrative_id), audience=audience, narrative_type=narrative_type)
        return narrative

    def build_narratives(
        self,
        audiences: list[ExplanationLayer],
        correlation_id: str = "",
    ) -> list[ExplanationNarrative]:
        """Build narratives for multiple audiences.

        Maps each audience layer to an appropriate narrative type
        and delegates to build_narrative.

        Args:
            audiences: The target audience layers.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of built ExplanationNarrative instances.
        """
        narratives: list[ExplanationNarrative] = []
        for audience in audiences:
            narrative_type = _AUDIENCE_NARRATIVE_MAP.get(audience.value, "SUMMARY")
            narrative = self.build_narrative(
                narrative_type=narrative_type,
                audience=audience.value,
                context={},
                correlation_id=correlation_id,
            )
            narratives.append(narrative)
        log.info("Narratives built", count=len(narratives), audiences=[a.value for a in audiences])
        return narratives

    def get_narrative(self, narrative_id: str) -> ExplanationNarrative | None:
        """Get a narrative by its ID.

        Args:
            narrative_id: The narrative identifier.

        Returns:
            The ExplanationNarrative if found, None otherwise.
        """
        for n in self._narratives:
            if str(n.narrative_id) == narrative_id:
                return n
        return None

    def get_all(self) -> list[ExplanationNarrative]:
        """Get all built narratives.

        Returns:
            List of all ExplanationNarrative instances.
        """
        return list(self._narratives)

    def clear(self) -> None:
        """Clear all built narratives."""
        self._narratives.clear()
        log.info("Narratives cleared")

    def count(self) -> int:
        """Get the total number of built narratives.

        Returns:
            The number of narratives.
        """
        return len(self._narratives)
