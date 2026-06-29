"""GovernanceAuditPackage — immutable audit package builder.

Creates immutable audit packages containing the complete
review record for governance and compliance purposes.
Deterministic placeholder.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

import structlog

from adip.review.contracts.models import GovernanceAuditPackage as GovernanceAuditPackageModel

log = structlog.get_logger(__name__)


class GovernanceAuditPackage:
    """Creates immutable audit packages for governance.

    Packages contain:
    - Review Package (recommendation + explanation decisions)
    - Reviewer Decisions (each reviewer's decision)
    - Comments (all reviewer comments)
    - Workflow (approval workflow details)
    - Timeline (chronological event history)
    - Policy Evaluations (all policy check results)

    Each package is hashed for audit integrity.

    Deterministic placeholder implementation.
    """

    def __init__(self) -> None:
        self._packages: dict[str, GovernanceAuditPackageModel] = {}

    def create_package(
        self,
        decision_id: str,
        review_package: dict[str, Any] | None = None,
        reviewer_decisions: list[dict[str, Any]] | None = None,
        comments: list[dict[str, Any]] | None = None,
        workflow: dict[str, Any] | None = None,
        timeline: list[dict[str, Any]] | None = None,
        policy_evaluations: list[dict[str, Any]] | None = None,
        correlation_id: str = "",
    ) -> GovernanceAuditPackageModel:
        """Create an immutable audit package.

        Args:
            decision_id: The decision identifier.
            review_package: The original review package data.
            reviewer_decisions: Decisions made by each reviewer.
            comments: Reviewer comments.
            workflow: The approval workflow details.
            timeline: Timeline of review events.
            policy_evaluations: Policy evaluation results.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            GovernanceAuditPackageModel with hash for integrity.
        """
        did = uuid.UUID(decision_id) if isinstance(decision_id, str) else decision_id

        package_data = {
            "review_package": review_package or {},
            "reviewer_decisions": reviewer_decisions or [],
            "comments": comments or [],
            "workflow": workflow or {},
            "timeline": timeline or [],
            "policy_evaluations": policy_evaluations or [],
        }

        content_hash = self._compute_hash(package_data)

        package = GovernanceAuditPackageModel(
            decision_id=did,
            review_package=package_data["review_package"],
            reviewer_decisions=package_data["reviewer_decisions"],
            comments=package_data["comments"],
            workflow=package_data["workflow"],
            timeline=package_data["timeline"],
            policy_evaluations=package_data["policy_evaluations"],
            hash=content_hash,
        )
        pid = str(package.package_id)
        self._packages[pid] = package
        log.info(
            "audit_package.created",
            package_id=pid,
            decision_id=decision_id,
            hash=content_hash[:16],
            correlation_id=correlation_id,
        )
        return package

    def _compute_hash(self, data: dict[str, Any]) -> str:
        raw = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode()).hexdigest()

    def get_package(self, package_id: str) -> GovernanceAuditPackageModel | None:
        """Get an audit package by ID.

        Args:
            package_id: The package identifier.

        Returns:
            GovernanceAuditPackageModel if found, None otherwise.
        """
        return self._packages.get(package_id)

    def verify_package(self, package_id: str) -> bool:
        """Verify the integrity of an audit package.

        Recomputes the hash and compares with stored hash.

        Args:
            package_id: The package identifier.

        Returns:
            True if the package hash is valid, False otherwise.
        """
        package = self._packages.get(package_id)
        if package is None:
            return False
        package_data = {
            "review_package": package.review_package,
            "reviewer_decisions": package.reviewer_decisions,
            "comments": package.comments,
            "workflow": package.workflow,
            "timeline": package.timeline,
            "policy_evaluations": package.policy_evaluations,
        }
        computed = self._compute_hash(package_data)
        return computed == package.hash

    def count(self) -> int:
        """Get the number of audit packages.

        Returns:
            The count of audit packages.
        """
        return len(self._packages)

    def clear(self) -> None:
        """Clear all audit packages."""
        self._packages.clear()
