"""ReviewValidator — deterministic validation for review entities.

Validates review packages, reviewers, policies, and workflows
against required fields and structural constraints.
"""

from __future__ import annotations

from typing import Any

import structlog

log = structlog.get_logger(__name__)


class ReviewValidator:
    """Validates review-related entities with deterministic checks."""

    def validate_review_package(
        self,
        package: Any,
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Validate a review package has required decisions."""
        errors: list[str] = []
        warnings: list[str] = []
        package_id: str = ""

        if package is None:
            errors.append("Package is None")
        else:
            package_id = str(getattr(package, "package_id", ""))

            rec = getattr(package, "recommendation_decision", None)
            if not rec:
                errors.append("Package is missing recommendation_decision")
            elif not isinstance(rec, dict) or not rec:
                warnings.append("recommendation_decision is empty")

            expl = getattr(package, "explanation_decision", None)
            if not expl:
                errors.append("Package is missing explanation_decision")
            elif not isinstance(expl, dict) or not expl:
                warnings.append("explanation_decision is empty")

        valid = len(errors) == 0
        log.info(
            "review_validator.validate_review_package",
            valid=valid,
            errors=len(errors),
            warnings=len(warnings),
            correlation_id=correlation_id,
        )
        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
            "package_id": package_id,
        }

    def validate_reviewer(
        self,
        reviewer: Any,
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Validate a reviewer has required fields."""
        errors: list[str] = []
        warnings: list[str] = []

        if reviewer is None:
            errors.append("Reviewer is None")
        else:
            if not getattr(reviewer, "name", None):
                errors.append("Reviewer is missing name")

            if not getattr(reviewer, "role", None):
                errors.append("Reviewer is missing role")

            is_active = getattr(reviewer, "is_active", None)
            if is_active is False:
                warnings.append("Reviewer is not active")
            elif is_active is None:
                errors.append("Reviewer is missing is_active")

        valid = len(errors) == 0
        log.info(
            "review_validator.validate_reviewer",
            valid=valid,
            errors=len(errors),
            warnings=len(warnings),
            correlation_id=correlation_id,
        )
        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
        }

    def validate_policy(
        self,
        policy: Any,
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Validate a review policy has required configuration."""
        errors: list[str] = []
        warnings: list[str] = []

        if policy is None:
            errors.append("Policy is None")
        else:
            outcomes = getattr(policy, "allowed_outcomes", None)
            if not outcomes:
                errors.append("Policy is missing allowed_outcomes")
            elif not isinstance(outcomes, list) or not outcomes:
                warnings.append("allowed_outcomes is empty")

            roles = getattr(policy, "required_reviewer_roles", None)
            if not roles:
                errors.append("Policy is missing required_reviewer_roles")
            elif not isinstance(roles, list) or not roles:
                warnings.append("required_reviewer_roles is empty")

        valid = len(errors) == 0
        log.info(
            "review_validator.validate_policy",
            valid=valid,
            errors=len(errors),
            warnings=len(warnings),
            correlation_id=correlation_id,
        )
        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
        }

    def validate_workflow(
        self,
        workflow: Any,
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Validate an approval workflow has required fields."""
        errors: list[str] = []
        warnings: list[str] = []

        if workflow is None:
            errors.append("Workflow is None")
        else:
            if not getattr(workflow, "workflow_type", None):
                errors.append("Workflow is missing workflow_type")

            steps = getattr(workflow, "steps", None)
            if not steps:
                errors.append("Workflow is missing steps")
            elif not isinstance(steps, list) or not steps:
                warnings.append("steps is empty")

        valid = len(errors) == 0
        log.info(
            "review_validator.validate_workflow",
            valid=valid,
            errors=len(errors),
            warnings=len(warnings),
            correlation_id=correlation_id,
        )
        return {
            "valid": valid,
            "errors": errors,
            "warnings": warnings,
        }

    def validate_all(
        self,
        package: Any,
        reviewer: Any,
        policy: Any,
        workflow: Any,
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Run all four validators and aggregate results."""
        package_result = self.validate_review_package(package, correlation_id)
        reviewer_result = self.validate_reviewer(reviewer, correlation_id)
        policy_result = self.validate_policy(policy, correlation_id)
        workflow_result = self.validate_workflow(workflow, correlation_id)

        all_valid = (
            package_result["valid"]
            and reviewer_result["valid"]
            and policy_result["valid"]
            and workflow_result["valid"]
        )
        all_errors = (
            package_result["errors"]
            + reviewer_result["errors"]
            + policy_result["errors"]
            + workflow_result["errors"]
        )
        all_warnings = (
            package_result["warnings"]
            + reviewer_result["warnings"]
            + policy_result["warnings"]
            + workflow_result["warnings"]
        )

        log.info(
            "review_validator.validate_all",
            valid=all_valid,
            total_errors=len(all_errors),
            total_warnings=len(all_warnings),
            correlation_id=correlation_id,
        )
        return {
            "valid": all_valid,
            "errors": all_errors,
            "warnings": all_warnings,
            "package": package_result,
            "reviewer": reviewer_result,
            "policy": policy_result,
            "workflow": workflow_result,
        }
