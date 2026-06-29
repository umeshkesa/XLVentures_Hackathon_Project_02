"""Workflow Engine exception hierarchy."""

from __future__ import annotations


class WorkflowException(Exception):
    """Base exception for all workflow errors."""
    def __init__(self, message: str = "Workflow error") -> None:
        self.message = message
        super().__init__(self.message)


class WorkflowValidationException(WorkflowException):
    """Raised when a workflow request or state fails validation."""
    def __init__(self, message: str = "Workflow validation error") -> None:
        super().__init__(message)


class TaskExecutionException(WorkflowException):
    """Raised when a task fails during execution."""
    def __init__(
        self,
        task_id: str | None = None,
        message: str = "Task execution error",
    ) -> None:
        self.task_id = task_id
        super().__init__(message)


class SchedulingException(WorkflowException):
    """Raised when the scheduler cannot schedule a task."""
    def __init__(self, message: str = "Scheduling error") -> None:
        super().__init__(message)


class RetryException(WorkflowException):
    """Raised when a retry operation is not possible or fails."""
    def __init__(self, message: str = "Retry error") -> None:
        super().__init__(message)


class ApprovalException(WorkflowException):
    """Raised when an approval operation fails."""
    def __init__(self, message: str = "Approval error") -> None:
        super().__init__(message)


class StateTransitionException(WorkflowException):
    """Raised when an illegal workflow state transition is attempted."""
    def __init__(
        self,
        from_state: str = "",
        to_state: str = "",
        message: str = "",
    ) -> None:
        self.from_state = from_state
        self.to_state = to_state
        if not message:
            message = f"Illegal transition: {from_state} → {to_state}"
        super().__init__(message)
