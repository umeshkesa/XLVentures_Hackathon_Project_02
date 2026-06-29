"""ExplanationReadiness — determines explanation readiness.

Assesses whether an explanation is ready for use, requires
further review, or is incomplete. Deterministic placeholder.
"""

from __future__ import annotations

import structlog

log = structlog.get_logger(__name__)


class ExplanationReadiness:
    """Determines readiness of explanation decisions.

    Deterministic placeholder that assesses readiness based on
    confidence, quality, review results, and compliance status.
    """

    def assess(
        self,
        confidence_score: float = 0.0,
        quality_score: float = 0.0,
        review_results: dict[str, list[str]] | None = None,
        correlation_id: str = "",
        compliance_status: str = "",
    ) -> str:
        """Assess the readiness of an explanation.

        Rules:
        - "NON_COMPLIANT" if compliance_status == "NON_COMPLIANT".
        - "READY" if confidence >= 0.7 and quality >= 0.7 and no review warnings.
        - "REVIEW_REQUIRED" if confidence >= 0.5 and quality >= 0.5.
        - "INCOMPLETE" otherwise.

        Args:
            confidence_score: Overall confidence score (0.0-1.0).
            quality_score: Overall quality score (0.0-1.0).
            review_results: Dictionary of review warnings per category.
            correlation_id: Optional correlation ID for tracing.
            compliance_status: Compliance status string (e.g. "NON_COMPLIANT").

        Returns:
            String readiness status: "NON_COMPLIANT", "READY",
            "REVIEW_REQUIRED", or "INCOMPLETE".
        """
        if compliance_status == "NON_COMPLIANT":
            log.info(
                "readiness.assess",
                status="NON_COMPLIANT",
                confidence=confidence_score,
                quality=quality_score,
                compliance_status=compliance_status,
                correlation_id=correlation_id,
            )
            return "NON_COMPLIANT"

        has_warnings = any(
            len(warnings) > 0
            for warnings in (review_results or {}).values()
        )

        if confidence_score >= 0.7 and quality_score >= 0.7 and not has_warnings:
            log.info(
                "readiness.assess",
                status="READY",
                confidence=confidence_score,
                quality=quality_score,
                correlation_id=correlation_id,
            )
            return "READY"

        if confidence_score >= 0.5 and quality_score >= 0.5:
            log.info(
                "readiness.assess",
                status="REVIEW_REQUIRED",
                confidence=confidence_score,
                quality=quality_score,
                has_warnings=has_warnings,
                correlation_id=correlation_id,
            )
            return "REVIEW_REQUIRED"

        log.info(
            "readiness.assess",
            status="INCOMPLETE",
            confidence=confidence_score,
            quality=quality_score,
            correlation_id=correlation_id,
        )
        return "INCOMPLETE"
