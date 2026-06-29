"""AudienceFormatter — formats narratives for target audiences.

Deterministic placeholder that applies prefix-based formatting
to ExplanationNarrative instances for specific audience layers.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.explainability.contracts.models import ExplanationNarrative
from adip.explainability.enums import ExplanationLayer
from adip.explainability.execution.models import AudienceFormat

log = structlog.get_logger(__name__)

_AUDIENCE_PREFIXES: dict[str, str] = {
    "EXECUTIVE": "Executive summary format: ",
    "MANAGER": "Manager overview format: ",
    "ENGINEER": "Technical detail format: ",
    "OPERATOR": "Operator actionable format: ",
    "TECHNICIAN": "Technician procedure format: ",
    "AUDITOR": "Auditor compliance format: ",
    "DEVELOPER": "Developer system format: ",
}

_AUDIENCE_PROFILES: dict[str, dict[str, Any]] = {
    "EXECUTIVE": {"detail_level": "high", "technical_depth": 0.1, "template_name": "executive_briefing"},
    "MANAGER": {"detail_level": "high", "technical_depth": 0.3, "template_name": "manager_summary"},
    "ENGINEER": {"detail_level": "full", "technical_depth": 0.9, "template_name": "technical_deep_dive"},
    "OPERATOR": {"detail_level": "medium", "technical_depth": 0.5, "template_name": "operator_actions"},
    "TECHNICIAN": {"detail_level": "full", "technical_depth": 0.8, "template_name": "technician_guide"},
    "AUDITOR": {"detail_level": "full", "technical_depth": 0.6, "template_name": "audit_report"},
    "DEVELOPER": {"detail_level": "full", "technical_depth": 1.0, "template_name": "developer_docs"},
}


class AudienceFormatter:
    """Formats explanation narratives for specific audience layers.

    Deterministic placeholder that applies prefix-based formatting
    and returns audience format configurations.
    """

    def __init__(self) -> None:
        self._narratives: list[ExplanationNarrative] = []

    def format(
        self,
        narrative: ExplanationNarrative,
        audience: ExplanationLayer,
        correlation_id: str = "",
    ) -> ExplanationNarrative:
        """Format a narrative for a specific audience.

        Returns a copy of the narrative with content modified
        for the target audience using a deterministic prefix.

        Args:
            narrative: The narrative to format.
            audience: The target audience layer.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The formatted ExplanationNarrative.
        """
        prefix = _AUDIENCE_PREFIXES.get(audience.value, "")
        formatted = narrative.model_copy(deep=True)
        formatted.content = f"{prefix}{formatted.content}"
        formatted.summary = f"{prefix}{formatted.summary}"
        self._narratives.append(formatted)
        log.info("Narrative formatted", narrative_id=str(formatted.narrative_id), audience=audience.value)
        return formatted

    def format_batch(
        self,
        narratives: list[ExplanationNarrative],
        audience: ExplanationLayer,
        correlation_id: str = "",
    ) -> list[ExplanationNarrative]:
        """Format multiple narratives for a specific audience.

        Args:
            narratives: The narratives to format.
            audience: The target audience layer.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of formatted ExplanationNarrative instances.
        """
        formatted = [self.format(n, audience, correlation_id) for n in narratives]
        log.info("Batch formatted", count=len(formatted), audience=audience.value)
        return formatted

    def get_format(self, audience: str) -> AudienceFormat:
        """Get the format configuration for an audience.

        Args:
            audience: The audience identifier.

        Returns:
            AudienceFormat with audience format configuration.
        """
        profile = _AUDIENCE_PROFILES.get(audience, {"detail_level": "medium", "technical_depth": 0.5})
        return AudienceFormat(
            audience=audience,
            template_name=profile.get("template_name", "standard"),
            detail_level=profile.get("detail_level", "medium"),
            technical_depth=profile.get("technical_depth", 0.5),
            format_preferences={"prefix": _AUDIENCE_PREFIXES.get(audience, "")},
        )

    def get_audience_profiles(self) -> dict[str, dict[str, Any]]:
        """Get all audience format profiles.

        Returns:
            Dictionary of audience profiles.
        """
        return dict(_AUDIENCE_PROFILES)
