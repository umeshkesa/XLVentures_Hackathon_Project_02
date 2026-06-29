"""ReviewExportPackage — export packages for review data.

Supports multiple export profiles: REST API, Dashboard,
Audit Report, Compliance Report, and JSON.
Deterministic placeholder.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import structlog

log = structlog.get_logger(__name__)


class ExportProfile(StrEnum):
    REST_API = "REST_API"
    DASHBOARD = "DASHBOARD"
    AUDIT_REPORT = "AUDIT_REPORT"
    COMPLIANCE_REPORT = "COMPLIANCE_REPORT"
    JSON = "JSON"


class ReviewExportPackageRecord:
    """Record of an export package."""

    def __init__(
        self,
        export_id: str,
        decision_id: str,
        profile: ExportProfile,
        data: dict[str, Any],
    ) -> None:
        self.export_id = export_id
        self.decision_id = decision_id
        self.profile = profile
        self.data = data
        self.created_at = datetime.now(UTC)


class ReviewExportPackage:
    """Creates export packages for review data.

    Supports multiple export profiles:
    - REST_API: lightweight JSON for API consumption
    - DASHBOARD: structured for dashboard display
    - AUDIT_REPORT: comprehensive for audit purposes
    - COMPLIANCE_REPORT: focused on compliance data
    - JSON: raw JSON export

    Deterministic placeholder implementation.
    """

    def __init__(self) -> None:
        self._exports: dict[str, ReviewExportPackageRecord] = {}

    def create_export(
        self,
        decision_id: str,
        profile: ExportProfile = ExportProfile.JSON,
        review_data: dict[str, Any] | None = None,
        correlation_id: str = "",
    ) -> ReviewExportPackageRecord:
        """Create an export package for a review decision.

        Args:
            decision_id: The decision identifier.
            profile: The export profile type.
            review_data: The review data to export.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReviewExportPackageRecord with profile-specific data.
        """
        data = self._build_export_data(profile, review_data or {})
        record = ReviewExportPackageRecord(
            export_id=str(uuid.uuid4()),
            decision_id=decision_id,
            profile=profile,
            data=data,
        )
        self._exports[record.export_id] = record
        log.info(
            "export.created",
            export_id=record.export_id,
            decision_id=decision_id,
            profile=profile.value,
            correlation_id=correlation_id,
        )
        return record

    def _build_export_data(
        self,
        profile: ExportProfile,
        review_data: dict[str, Any],
    ) -> dict[str, Any]:
        if profile == ExportProfile.REST_API:
            return {
                "decision_id": review_data.get("decision_id", ""),
                "outcome": review_data.get("outcome", ""),
                "confidence": review_data.get("confidence", 0.0),
                "summary": review_data.get("summary", ""),
                "timestamp": datetime.now(UTC).isoformat(),
            }
        elif profile == ExportProfile.DASHBOARD:
            return {
                "title": review_data.get("title", "Review Dashboard"),
                "decision_id": review_data.get("decision_id", ""),
                "outcome": review_data.get("outcome", ""),
                "confidence": review_data.get("confidence", 0.0),
                "governance_confidence": review_data.get("governance_confidence", 0.0),
                "domain": review_data.get("domain", ""),
                "reviewer": review_data.get("reviewer", ""),
                "duration_ms": review_data.get("duration_ms", 0),
                "charts": review_data.get("charts", {}),
                "timestamp": datetime.now(UTC).isoformat(),
            }
        elif profile == ExportProfile.AUDIT_REPORT:
            return {
                "audit_title": f"Audit Report - {review_data.get('decision_id', '')}",
                "decision_id": review_data.get("decision_id", ""),
                "outcome": review_data.get("outcome", ""),
                "reviewer_decisions": review_data.get("reviewer_decisions", []),
                "comments": review_data.get("comments", []),
                "workflow": review_data.get("workflow", {}),
                "timeline": review_data.get("timeline", []),
                "policy_evaluations": review_data.get("policy_evaluations", []),
                "confidence": review_data.get("confidence", {}),
                "version": review_data.get("version", {}),
                "hash": review_data.get("hash", ""),
                "timestamp": datetime.now(UTC).isoformat(),
            }
        elif profile == ExportProfile.COMPLIANCE_REPORT:
            return {
                "compliance_title": f"Compliance Report - {review_data.get('decision_id', '')}",
                "decision_id": review_data.get("decision_id", ""),
                "compliance_status": review_data.get("compliance_status", ""),
                "policy_checks": review_data.get("policy_checks", []),
                "escalations": review_data.get("escalations", []),
                "sla_compliance": review_data.get("sla_compliance", True),
                "separation_of_duties": review_data.get("separation_of_duties", True),
                "audit_completeness": review_data.get("audit_completeness", True),
                "timestamp": datetime.now(UTC).isoformat(),
            }
        else:  # JSON
            return {
                **review_data,
                "export_timestamp": datetime.now(UTC).isoformat(),
            }

    def get_export(self, export_id: str) -> ReviewExportPackageRecord | None:
        """Get an export package by ID.

        Args:
            export_id: The export identifier.

        Returns:
            ReviewExportPackageRecord if found, None otherwise.
        """
        return self._exports.get(export_id)

    def get_exports_for_decision(
        self,
        decision_id: str,
    ) -> list[ReviewExportPackageRecord]:
        """Get all exports for a decision.

        Args:
            decision_id: The decision identifier.

        Returns:
            List of ReviewExportPackageRecord for the decision.
        """
        return [e for e in self._exports.values() if e.decision_id == decision_id]

    def count(self) -> int:
        """Get the number of export packages.

        Returns:
            The count of export packages.
        """
        return len(self._exports)

    def clear(self) -> None:
        """Clear all export packages."""
        self._exports.clear()
