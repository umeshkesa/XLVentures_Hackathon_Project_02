"""Exception definitions for the Decision Review Layer.

Defines all exception types used across review operations
for consistent error handling and reporting.
"""

from __future__ import annotations

from typing import Any


class ReviewException(Exception):
    """Base exception for all review errors.

    All review-specific exceptions inherit from this class
    for consistent error handling.
    """

    def __init__(
        self,
        message: str = "Review error occurred",
        code: str = "REVIEW_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class ApprovalException(ReviewException):
    """Exception raised for approval errors.

    Raised when approval workflow operations, step execution,
    or approval validation fails.
    """

    def __init__(
        self,
        message: str = "Approval error occurred",
        code: str = "APPROVAL_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)


class EscalationException(ReviewException):
    """Exception raised for escalation errors.

    Raised when escalation rules, target assignment,
    or escalation execution fails.
    """

    def __init__(
        self,
        message: str = "Escalation error occurred",
        code: str = "ESCALATION_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)


class ReviewValidationException(ReviewException):
    """Exception raised for review validation errors.

    Raised when review request, session, decision, or
    outcome validation fails.
    """

    def __init__(
        self,
        message: str = "Review validation error occurred",
        code: str = "REVIEW_VALIDATION_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)
