"""ExplanationCompliance — validates explanation compliance.

Checks regulatory, citation, governance, and audit requirements
for explanation packages. Deterministic placeholder implementation.
"""

from __future__ import annotations

from typing import Any

import structlog

log = structlog.get_logger(__name__)


class ExplanationCompliance:
    """Validates compliance of explanation packages.

    Deterministic placeholder that checks regulatory fields,
    mandatory citations, governance rules, and audit requirements.
    """

    def validate_regulatory_fields(
        self,
        explanation_id: str = "",
        package: Any = None,
        narratives: list[Any] | None = None,
        citations: list[Any] | None = None,
        correlation_id: str = "",
    ) -> dict[str, list[str]]:
        """Check all required regulatory fields are present.

        Validates that the package has a result_id, package_id,
        at least one narrative, and at least one citation.

        Args:
            explanation_id: The explanation identifier.
            package: The explanation package to validate.
            narratives: List of narratives.
            citations: List of citations.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dictionary mapping field names to lists of violation strings.
        """
        violations: dict[str, list[str]] = {}
        package_result_id = getattr(package, "result_id", None) if package else None
        package_package_id = getattr(package, "package_id", None) if package else None

        if not package_result_id:
            violations["result_id"] = ["Missing result_id in package"]
        if not package_package_id:
            violations["package_id"] = ["Missing package_id in package"]
        if not narratives:
            violations["narratives"] = ["At least one narrative is required"]
        if not citations:
            violations["citations"] = ["At least one citation is required"]

        log.info(
            "compliance.validate_regulatory",
            explanation_id=explanation_id,
            violations=sum(len(v) for v in violations.values()),
            correlation_id=correlation_id,
        )
        return violations

    def validate_mandatory_citations(
        self,
        citations: list[Any] | None = None,
        correlation_id: str = "",
    ) -> list[str]:
        """Check that mandatory citation types are present.

        Returns violations if citations are missing evidence,
        reasoning, or recommendation types.

        Args:
            citations: List of citation objects.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of violation strings.
        """
        violations: list[str] = []
        if not citations:
            return ["No citations provided"]

        citation_types = {
            getattr(c, "citation_type", None) for c in citations
        }

        if "EVIDENCE" not in citation_types:
            violations.append("Missing mandatory citation type: EVIDENCE")
        if "REASONING" not in citation_types:
            violations.append("Missing mandatory citation type: REASONING")
        if "RECOMMENDATION" not in citation_types:
            violations.append("Missing mandatory citation type: RECOMMENDATION")

        log.info(
            "compliance.validate_citations",
            citation_types=len(citation_types),
            violations=len(violations),
            correlation_id=correlation_id,
        )
        return violations

    def validate_governance_rules(
        self,
        package: Any = None,
        metadata: Any = None,
        correlation_id: str = "",
    ) -> list[str]:
        """Check governance rules for the package.

        Validates that reasoning_summary is non-empty,
        recommendation_summary is non-empty, and
        overall_confidence is greater than 0.

        Args:
            package: The explanation package to validate.
            metadata: The explanation metadata.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of violation strings.
        """
        violations: list[str] = []
        if package is None:
            return ["No package provided for governance validation"]

        reasoning = getattr(package, "reasoning_summary", "")
        recommendation = getattr(package, "recommendation_summary", "")
        confidence = getattr(package, "overall_confidence", 0.0)

        if not reasoning:
            violations.append("reasoning_summary must be non-empty")
        if not recommendation:
            violations.append("recommendation_summary must be non-empty")
        if confidence <= 0.0:
            violations.append("overall_confidence must be greater than 0")

        log.info(
            "compliance.validate_governance",
            reasoning_empty=not reasoning,
            recommendation_empty=not recommendation,
            confidence=confidence,
            violations=len(violations),
            correlation_id=correlation_id,
        )
        return violations

    def validate_audit_requirements(
        self,
        traces: list[Any] | None = None,
        correlation_id: str = "",
    ) -> list[str]:
        """Check that all required trace stages are present.

        Validates that the traces contain narrative, citation,
        formatting, and timeline stages.

        Args:
            traces: List of trace records.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of violation strings.
        """
        violations: list[str] = []
        if not traces:
            return ["No trace records provided"]

        required_stages = {"narrative", "citation", "formatting", "timeline"}
        present_stages = {
            getattr(t, "stage_name", "").lower() for t in traces
        }

        for stage in sorted(required_stages):
            if stage not in present_stages:
                violations.append(f"Missing required trace stage: {stage}")

        log.info(
            "compliance.validate_audit",
            present_stages=len(present_stages),
            violations=len(violations),
            correlation_id=correlation_id,
        )
        return violations

    def assess_compliance(
        self,
        explanation_id: str = "",
        package: Any = None,
        narratives: list[Any] | None = None,
        citations: list[Any] | None = None,
        traces: list[Any] | None = None,
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Run all compliance validations and return a combined result.

        Executes regulatory field, mandatory citation, governance,
        and audit requirement checks.

        Args:
            explanation_id: The explanation identifier.
            package: The explanation package to validate.
            narratives: List of narratives.
            citations: List of citations.
            traces: List of trace records.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dictionary with compliance result containing:
                - compliant: bool — whether all validations passed.
                - violations: dict[str, list[str]] — per-category violations.
                - status: str — "COMPLIANT" or "NON_COMPLIANT".
        """
        violations: dict[str, list[str]] = {}

        regulatory = self.validate_regulatory_fields(
            explanation_id, package, narratives, citations, correlation_id,
        )
        if regulatory:
            violations["regulatory_fields"] = [
                f"{k}: {', '.join(v)}" for k, v in regulatory.items()
            ]

        citation_violations = self.validate_mandatory_citations(citations, correlation_id)
        if citation_violations:
            violations["mandatory_citations"] = citation_violations

        governance_violations = self.validate_governance_rules(package, None, correlation_id)
        if governance_violations:
            violations["governance_rules"] = governance_violations

        audit_violations = self.validate_audit_requirements(traces, correlation_id)
        if audit_violations:
            violations["audit_requirements"] = audit_violations

        compliant = len(violations) == 0
        status = "COMPLIANT" if compliant else "NON_COMPLIANT"

        log.info(
            "compliance.assess",
            explanation_id=explanation_id,
            compliant=compliant,
            category_count=len(violations),
            correlation_id=correlation_id,
        )

        return {
            "compliant": compliant,
            "violations": violations,
            "status": status,
        }
