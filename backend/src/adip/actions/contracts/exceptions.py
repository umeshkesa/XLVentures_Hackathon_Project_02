"""Exception definitions for the Action Manager.

Defines all exception types used across action operations
for consistent error handling and reporting.
"""

from __future__ import annotations

from typing import Any


class ActionException(Exception):
    """Base exception for all action errors.

    All action-specific exceptions inherit from this class
    for consistent error handling.
    """

    def __init__(
        self,
        message: str = "Action error occurred",
        code: str = "ACTION_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class PlanningException(ActionException):
    """Exception raised for action planning errors.

    Raised when plan generation, step creation, or
    overall planning logic fails.
    """

    def __init__(
        self,
        message: str = "Planning error occurred",
        code: str = "PLANNING_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)


class DependencyException(ActionException):
    """Exception raised for dependency resolution errors.

    Raised when dependency detection, resolution, or
    validation fails during planning.
    """

    def __init__(
        self,
        message: str = "Dependency error occurred",
        code: str = "DEPENDENCY_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)


class ScheduleException(ActionException):
    """Exception raised for scheduling errors.

    Raised when schedule creation, validation, or
    constraint checking fails.
    """

    def __init__(
        self,
        message: str = "Schedule error occurred",
        code: str = "SCHEDULE_ERROR",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message=message, code=code, details=details)
