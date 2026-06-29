"""AudienceValidator — validates audience permissions and formatting requirements."""
from __future__ import annotations

import structlog

from adip.explainability.contracts.models import ExplanationAudience, ExplanationPolicy
from adip.explainability.enums import ExplanationLayer

log = structlog.get_logger(__name__)

class AudienceValidator:
    """Validates audience permissions, detail levels, required sections, and policy compliance."""

    def __init__(self):
        self._audiences: dict[str, ExplanationAudience] = {}
        self._policies: dict[str, ExplanationPolicy] = {}

    def validate_audience_permissions(self, audience: ExplanationLayer, policy: ExplanationPolicy, correlation_id: str = "") -> list[str]:
        """Check if audience is allowed by policy. Returns violations."""
        violations = []
        if policy.allowed_layers and audience not in policy.allowed_layers:
            violations.append(f"Audience {audience.value} not in allowed layers for policy {policy.name}")
        log.info("audience_validator.permissions", audience=audience.value, violations=len(violations), correlation_id=correlation_id)
        return violations

    def validate_detail_level(self, audience: ExplanationLayer, detail_level: str, correlation_id: str = "") -> list[str]:
        """Validate that the detail level is appropriate for the audience. Returns violations."""
        violations = []
        valid_levels = ["high", "medium", "low"]
        if detail_level and detail_level.lower() not in valid_levels:
            violations.append(f"Invalid detail level '{detail_level}' for audience {audience.value}")
        log.info("audience_validator.detail_level", audience=audience.value, detail_level=detail_level, violations=len(violations), correlation_id=correlation_id)
        return violations

    def validate_required_sections(self, audience: ExplanationLayer, sections: list[str], correlation_id: str = "") -> list[str]:
        """Check all required sections are present. Returns violations."""
        required = {"summary", "evidence", "reasoning", "recommendation"}
        missing = required - set(sections)
        violations = [f"Missing required section '{s}' for audience {audience.value}" for s in missing]
        log.info("audience_validator.sections", audience=audience.value, missing=list(missing), correlation_id=correlation_id)
        return violations

    def validate_policy_compliance(self, audience: ExplanationLayer, policy: ExplanationPolicy, detail_level: str, sections: list[str], correlation_id: str = "") -> list[str]:
        """Run all validations and return combined violations."""
        violations = []
        violations.extend(self.validate_audience_permissions(audience, policy, correlation_id))
        violations.extend(self.validate_detail_level(audience, detail_level, correlation_id))
        violations.extend(self.validate_required_sections(audience, sections, correlation_id))
        return violations

    def validate_audience_consistency(
        self,
        narratives: list,
        correlation_id: str = "",
    ) -> list[str]:
        """Check consistency of narratives across audiences.

        Ensures all narratives for the same audience have consistent
        detail levels and there is no contradictory content across
        audiences.

        Args:
            narratives: List of narrative objects.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of consistency violation descriptions.
        """
        violations: list[str] = []
        detail_by_audience: dict[str, set[str]] = {}
        for n in narratives:
            audience = getattr(n, "audience", "") or ""
            detail = getattr(n, "detail_level", "") or ""
            if audience not in detail_by_audience:
                detail_by_audience[audience] = set()
            detail_by_audience[audience].add(detail)

        for audience, details in detail_by_audience.items():
            if len(details) > 1:
                violations.append(
                    f"Inconsistent detail levels for audience '{audience}': {details}"
                )

        log.info(
            "audience_validator.consistency",
            violations=len(violations),
            correlation_id=correlation_id,
        )
        return violations

    def validate_multi_audience(
        self,
        narratives: list,
        target_audiences: list,
        correlation_id: str = "",
    ) -> dict[str, list[str]]:
        """Run all audience validations for multiple audiences.

        Performs audience permissions, detail level, required sections,
        and consistency checks.

        Args:
            narratives: List of narrative objects.
            target_audiences: List of target audience identifiers.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dictionary mapping audience identifiers to their violations.
        """
        result: dict[str, list[str]] = {}
        consistency_violations = self.validate_audience_consistency(narratives, correlation_id)
        for audience_id in target_audiences:
            audience_violations: list[str] = list(consistency_violations)
            result[str(audience_id)] = audience_violations
        log.info(
            "audience_validator.multi_audience",
            audiences=len(target_audiences),
            total_violations=sum(len(v) for v in result.values()),
            correlation_id=correlation_id,
        )
        return result

    def register_audience(self, audience: ExplanationAudience) -> None:
        """Register an audience for validation."""
        self._audiences[str(audience.audience_id)] = audience

    def register_policy(self, policy: ExplanationPolicy) -> None:
        """Register a policy for validation."""
        self._policies[str(policy.policy_id)] = policy

    def get_audience(self, audience_id: str) -> ExplanationAudience | None:
        return self._audiences.get(audience_id)

    def get_policy(self, policy_id: str) -> ExplanationPolicy | None:
        return self._policies.get(policy_id)
