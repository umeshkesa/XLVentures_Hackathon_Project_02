"""Validation tests for Workflow Engine exceptions."""

from __future__ import annotations

from adip.workflow.contracts.exceptions import (
    ApprovalException,
    RetryException,
    SchedulingException,
    TaskExecutionException,
    WorkflowException,
    WorkflowValidationException,
)


class TestWorkflowExceptions:
    def test_base_exception(self) -> None:
        exc = WorkflowException("Base error")
        assert str(exc) == "Base error"
        assert isinstance(exc, Exception)

    def test_validation_exception(self) -> None:
        exc = WorkflowValidationException("Invalid workflow")
        assert str(exc) == "Invalid workflow"
        assert isinstance(exc, WorkflowException)

    def test_task_execution_exception(self) -> None:
        exc = TaskExecutionException(task_id="task-1", message="Task failed")
        assert exc.task_id == "task-1"
        assert str(exc) == "Task failed"
        assert isinstance(exc, WorkflowException)

    def test_scheduling_exception(self) -> None:
        exc = SchedulingException("Cannot schedule")
        assert str(exc) == "Cannot schedule"
        assert isinstance(exc, WorkflowException)

    def test_retry_exception(self) -> None:
        exc = RetryException("Retry limit reached")
        assert str(exc) == "Retry limit reached"
        assert isinstance(exc, WorkflowException)

    def test_approval_exception(self) -> None:
        exc = ApprovalException("Approval denied")
        assert str(exc) == "Approval denied"
        assert isinstance(exc, WorkflowException)

    def test_all_are_exceptions(self) -> None:
        assert issubclass(WorkflowException, Exception)
        assert issubclass(WorkflowValidationException, WorkflowException)
        assert issubclass(TaskExecutionException, WorkflowException)
        assert issubclass(SchedulingException, WorkflowException)
        assert issubclass(RetryException, WorkflowException)
        assert issubclass(ApprovalException, WorkflowException)
