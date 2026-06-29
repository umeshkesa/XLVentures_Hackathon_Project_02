"""Exception definitions for the Action Engine.

Defines all exception types used across execution operations
for consistent error handling and reporting.
"""

from __future__ import annotations

from typing import Any


class ExecutionException(Exception):
    """Base exception for all execution errors.

    All execution-specific exceptions inherit from this class
    for consistent error handling.
    """

    def __init__(
        self,
        message: str = "Execution error occurred",
        code: str = "EXECUTION_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class TaskExecutionException(ExecutionException):
    """Exception raised for task execution errors.

    Raised when a specific task fails during execution,
    including timeout, logic, or connectivity errors.
    """

    def __init__(
        self,
        message: str = "Task execution error occurred",
        code: str = "TASK_EXECUTION_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)


class RetryException(ExecutionException):
    """Exception raised for retry-related errors.

    Raised when a retry operation fails or the retry
    policy is exhausted.
    """

    def __init__(
        self,
        message: str = "Retry error occurred",
        code: str = "RETRY_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)


class CompensationException(ExecutionException):
    """Exception raised for compensation errors.

    Raised when a compensation or rollback operation fails
    during execution.
    """

    def __init__(
        self,
        message: str = "Compensation error occurred",
        code: str = "COMPENSATION_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)
