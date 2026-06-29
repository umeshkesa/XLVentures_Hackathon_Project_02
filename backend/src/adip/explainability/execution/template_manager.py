"""TemplateManager — manages narrative templates.

Deterministic placeholder that provides predefined narrative
templates for different explanation types.
"""

from __future__ import annotations

import structlog

from adip.explainability.execution.models import NarrativeTemplate

log = structlog.get_logger(__name__)

_PREDEFINED_TEMPLATES: dict[str, NarrativeTemplate] = {
    "executive": NarrativeTemplate(
        template_type="executive",
        name="Executive Briefing",
        description="High-level executive summary with strategic insights and key metrics.",
        sections=["summary", "key_findings", "recommendations", "risks", "next_steps"],
        audience="EXECUTIVE",
        metadata={"detail_level": "high", "technical_depth": 0.1},
    ),
    "technical": NarrativeTemplate(
        template_type="technical",
        name="Technical Deep Dive",
        description="Detailed technical analysis with system internals and root causes.",
        sections=["summary", "technical_analysis", "evidence", "reasoning", "conclusion"],
        audience="ENGINEER",
        metadata={"detail_level": "full", "technical_depth": 0.9},
    ),
    "audit": NarrativeTemplate(
        template_type="audit",
        name="Audit Report",
        description="Compliance-focused report with policy adherence and regulatory evidence.",
        sections=["summary", "compliance_check", "evidence", "policy_violations", "recommendations"],
        audience="AUDITOR",
        metadata={"detail_level": "full", "technical_depth": 0.6},
    ),
    "incident": NarrativeTemplate(
        template_type="incident",
        name="Incident Report",
        description="Incident-focused explanation with timeline, impact, and remediation steps.",
        sections=["summary", "timeline", "impact_analysis", "root_cause", "remediation"],
        audience="OPERATOR",
        metadata={"detail_level": "medium", "technical_depth": 0.5},
    ),
    "compliance": NarrativeTemplate(
        template_type="compliance",
        name="Compliance Summary",
        description="Compliance summary with regulatory findings and audit trail.",
        sections=["summary", "regulatory_findings", "evidence", "policy_check", "recommendations"],
        audience="MANAGER",
        metadata={"detail_level": "high", "technical_depth": 0.3},
    ),
}


class TemplateManager:
    """Manages predefined narrative templates.

    Deterministic placeholder that stores and retrieves
    NarrativeTemplate definitions for different explanation types.
    """

    def __init__(self) -> None:
        self._templates: dict[str, NarrativeTemplate] = dict(_PREDEFINED_TEMPLATES)

    def get_template(self, template_type: str) -> NarrativeTemplate | None:
        """Get a predefined template by type.

        Args:
            template_type: The template type (executive, technical, audit, incident, compliance).

        Returns:
            The NarrativeTemplate if found, None otherwise.
        """
        return self._templates.get(template_type)

    def list_templates(self) -> list[NarrativeTemplate]:
        """List all available templates.

        Returns:
            List of all registered NarrativeTemplate instances.
        """
        return list(self._templates.values())

    def register_template(self, template: NarrativeTemplate) -> None:
        """Register a new template.

        Args:
            template: The NarrativeTemplate to register.
        """
        self._templates[template.template_type] = template
        log.info("Template registered", template_type=template.template_type, name=template.name)

    def remove_template(self, template_id: str) -> None:
        """Remove a template by ID.

        Args:
            template_id: The template identifier to remove.
        """
        keys_to_remove = [k for k, v in self._templates.items() if v.template_id == template_id]
        for key in keys_to_remove:
            del self._templates[key]
            log.info("Template removed", template_id=template_id, template_type=key)

    def clear(self) -> None:
        """Clear all templates."""
        self._templates.clear()
        log.info("Templates cleared")

    def count(self) -> int:
        """Get the total number of registered templates.

        Returns:
            The number of templates.
        """
        return len(self._templates)
