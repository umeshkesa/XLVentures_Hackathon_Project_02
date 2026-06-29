"""ExplanationReview — reviews explanation quality and completeness.

Reviews narratives, citations, trace, audience, templates, and
policies for quality and completeness. Deterministic placeholder.
"""

from __future__ import annotations

from typing import Any

import structlog

log = structlog.get_logger(__name__)


class ExplanationReview:
    """Reviews explanation components for quality and completeness.

    Validates narratives, citations, trace records, audience types,
    templates, and policies. Returns warnings for each category.
    """

    def review_narratives(
        self,
        narratives: list[Any],
        correlation_id: str = "",
    ) -> list[str]:
        """Validate that each narrative has title, content, and audience.

        Args:
            narratives: List of narrative objects to review.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of warning strings for invalid narratives.
        """
        warnings: list[str] = []
        for i, narrative in enumerate(narratives):
            if not getattr(narrative, "title", None):
                warnings.append(f"Narrative at index {i} is missing title")
            if not getattr(narrative, "content", None):
                warnings.append(f"Narrative at index {i} is missing content")
            if not getattr(narrative, "audience", None):
                warnings.append(f"Narrative at index {i} is missing audience")
        log.info(
            "review.narratives",
            count=len(narratives),
            warnings=len(warnings),
            correlation_id=correlation_id,
        )
        return warnings

    def review_citations(
        self,
        citations: list[Any],
        correlation_id: str = "",
    ) -> list[str]:
        """Validate that each citation has source_id, source_type, and excerpt.

        Args:
            citations: List of citation objects to review.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of warning strings for invalid citations.
        """
        warnings: list[str] = []
        for i, citation in enumerate(citations):
            if not getattr(citation, "source_id", None):
                warnings.append(f"Citation at index {i} is missing source_id")
            if not getattr(citation, "source_type", None):
                warnings.append(f"Citation at index {i} is missing source_type")
            if not getattr(citation, "excerpt", None):
                warnings.append(f"Citation at index {i} is missing excerpt")
        log.info(
            "review.citations",
            count=len(citations),
            warnings=len(warnings),
            correlation_id=correlation_id,
        )
        return warnings

    def review_trace(
        self,
        traces: list[Any],
        correlation_id: str = "",
    ) -> list[str]:
        """Validate trace completeness.

        Checks that required stages are present in the trace records.

        Args:
            traces: List of trace record objects to review.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of warning strings for incomplete traces.
        """
        warnings: list[str] = []
        required_stages = {"INITIALIZED", "VALIDATION", "QUALITY", "CONFIDENCE", "COMPLETED"}
        present_stages = {getattr(t, "stage_name", "") for t in traces}
        missing = required_stages - present_stages
        for stage in sorted(missing):
            warnings.append(f"Trace is missing required stage '{stage}'")
        log.info(
            "review.trace",
            stages_present=len(present_stages),
            warnings=len(warnings),
            correlation_id=correlation_id,
        )
        return warnings

    def review_audience(
        self,
        audience: Any,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate audience type.

        Args:
            audience: Audience object or string to review.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of warning strings for invalid audience.
        """
        warnings: list[str] = []
        valid_audiences = {"EXECUTIVE", "MANAGER", "ENGINEER", "OPERATOR", "TECHNICIAN", "AUDITOR", "DEVELOPER"}
        audience_value = audience.value if hasattr(audience, "value") else str(audience)
        if audience_value not in valid_audiences:
            warnings.append(f"Invalid audience type: '{audience_value}'")
        log.info(
            "review.audience",
            audience=audience_value,
            warnings=len(warnings),
            correlation_id=correlation_id,
        )
        return warnings

    def review_templates(
        self,
        templates: list[Any],
        correlation_id: str = "",
    ) -> list[str]:
        """Validate that each template has sections.

        Args:
            templates: List of template objects to review.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of warning strings for invalid templates.
        """
        warnings: list[str] = []
        for i, template in enumerate(templates):
            sections = getattr(template, "sections", None)
            if not sections:
                warnings.append(f"Template at index {i} has no sections")
        log.info(
            "review.templates",
            count=len(templates),
            warnings=len(warnings),
            correlation_id=correlation_id,
        )
        return warnings

    def review_policies(
        self,
        policies: list[Any],
        correlation_id: str = "",
    ) -> list[str]:
        """Validate that each policy has allowed_layers.

        Args:
            policies: List of policy objects to review.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of warning strings for invalid policies.
        """
        warnings: list[str] = []
        for i, policy in enumerate(policies):
            allowed = getattr(policy, "allowed_layers", None)
            if not allowed:
                warnings.append(f"Policy at index {i} has no allowed_layers")
        log.info(
            "review.policies",
            count=len(policies),
            warnings=len(warnings),
            correlation_id=correlation_id,
        )
        return warnings

    def review(
        self,
        package: Any,
        narratives: list[Any],
        citations: list[Any],
        policies: list[Any],
        correlation_id: str = "",
    ) -> dict[str, list[str]]:
        """Run all reviews and return combined results per category.

        Args:
            package: The explanation package to review.
            narratives: List of narratives to review.
            citations: List of citations to review.
            policies: List of policies to review.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dictionary mapping category names to lists of warnings.
        """
        results: dict[str, list[str]] = {
            "narratives": self.review_narratives(narratives, correlation_id),
            "citations": self.review_citations(citations, correlation_id),
            "audience": self.review_audience(
                getattr(package, "primary_narrative", None),
                correlation_id,
            ) if getattr(package, "primary_narrative", None) else ["No primary narrative"],
            "policies": self.review_policies(policies, correlation_id),
        }
        total_warnings = sum(len(v) for v in results.values())
        log.info(
            "review.complete",
            categories=len(results),
            total_warnings=total_warnings,
            correlation_id=correlation_id,
        )
        return results
