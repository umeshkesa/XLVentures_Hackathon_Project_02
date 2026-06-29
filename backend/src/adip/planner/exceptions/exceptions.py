"""Planner-specific exceptions."""

from __future__ import annotations

from typing import Any

from adip.core.exceptions import BaseApplicationException


class PlannerException(BaseApplicationException):
    """Base exception for planner-related errors."""

    def __init__(self, message: str, code: str | None = None, details: Any | None = None):
        super().__init__(message, code=code or self.__class__.__name__, details=details)


class GoalAnalysisError(PlannerException):
    """Error during goal analysis."""

    pass


class ContextAnalysisError(PlannerException):
    """Error during context analysis."""

    pass


class CapabilityMatchingError(PlannerException):
    """Error during capability matching."""

    pass


class TaskDecompositionError(PlannerException):
    """Error during task decomposition."""

    pass


class PlanGenerationError(PlannerException):
    """Error during plan generation."""

    pass


class PlanValidationError(PlannerException):
    """Error during plan validation."""

    pass


class PlanOptimizationError(PlannerException):
    """Error during plan optimization."""

    pass


class ReplanningError(PlannerException):
    """Error during replanning."""

    pass


class ExecutionDispatchError(PlannerException):
    """Error during task execution dispatch."""

    pass


class PlannerInternalError(PlannerException):
    """A generic, unexpected internal error within the planner."""

    pass
