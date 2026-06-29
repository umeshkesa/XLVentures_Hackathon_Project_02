"""FailureClassifier — classifies execution failures into categories.

Classifies failures as transient, permanent, infrastructure,
dependency, policy, or timeout to determine the appropriate
recovery strategy.
"""

from __future__ import annotations

import structlog

from adip.execution.execution.models import FailureClassification

log = structlog.get_logger(__name__)

FAILURE_TYPES = [
    "transient",
    "permanent",
    "infrastructure",
    "dependency",
    "policy",
    "timeout",
]

TRANSIENT_PATTERNS = [
    "connection refused",
    "temporary",
    "retry",
    "throttl",
    "rate limit",
    "too many requests",
    "service unavailable",
    "busy",
    "timeout",
]

PERMANENT_PATTERNS = [
    "not found",
    "invalid",
    "unauthorized",
    "forbidden",
    "permission denied",
    "does not exist",
    "already exists",
]

INFRASTRUCTURE_PATTERNS = [
    "disk full",
    "out of memory",
    "no space",
    "connection lost",
    "network",
    "io error",
    "hardware",
]

DEPENDENCY_PATTERNS = [
    "dependency",
    "prerequisite",
    "precondition",
    "missing dependency",
    "unmet",
]

POLICY_PATTERNS = [
    "policy",
    "violation",
    "compliance",
    "governance",
    "not allowed",
    "restricted",
]


class FailureClassifier:
    """Classifies execution failures into retry/compensation categories."""

    def classify(
        self,
        task_id: str = "",
        error_message: str = "",
        correlation_id: str = "",
    ) -> FailureClassification:
        """Classify a failure based on the error message.

        Analyzes the error message against known patterns to
        determine the failure type and whether retry or
        compensation is appropriate.

        Args:
            task_id: The task ID that failed.
            error_message: The error message to classify.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A FailureClassification with type and recovery hints.
        """
        error_lower = error_message.lower() if error_message else ""

        failure_type, is_retryable, requires_comp, hint = self._classify_error(error_lower)

        classification = FailureClassification(
            task_id=task_id,
            failure_type=failure_type,
            error_message=error_message,
            is_retryable=is_retryable,
            requires_compensation=requires_comp,
            recovery_hint=hint,
        )
        log.info(
            "failure_classifier.classified",
            task_id=task_id,
            failure_type=failure_type,
            is_retryable=is_retryable,
            correlation_id=correlation_id,
        )
        return classification

    def _classify_error(
        self,
        error_lower: str,
    ) -> tuple[str, bool, bool, str]:
        """Classify error message into a failure type.

        Returns:
            Tuple of (failure_type, is_retryable, requires_compensation, recovery_hint).
        """
        for pattern in TIMEOUT_PATTERNS:
            if pattern in error_lower:
                return ("timeout", True, False, "Retry with increased timeout")

        for pattern in TRANSIENT_PATTERNS:
            if pattern in error_lower:
                return ("transient", True, False, "Retry with backoff")

        for pattern in INFRASTRUCTURE_PATTERNS:
            if pattern in error_lower:
                return ("infrastructure", False, False, "Contact infrastructure team")

        for pattern in DEPENDENCY_PATTERNS:
            if pattern in error_lower:
                return ("dependency", False, False, "Resolve dependency and retry")

        for pattern in POLICY_PATTERNS:
            if pattern in error_lower:
                return ("policy", False, False, "Review policy and request exception")

        for pattern in PERMANENT_PATTERNS:
            if pattern in error_lower:
                return ("permanent", False, True, "Manual intervention required")

        return ("transient", True, False, "Retry with default backoff")


TIMEOUT_PATTERNS = [
    "timeout",
    "timed out",
    "timedout",
    "deadline exceeded",
    "request timeout",
]
