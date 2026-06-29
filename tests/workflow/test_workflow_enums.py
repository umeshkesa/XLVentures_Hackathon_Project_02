"""Validation tests for Workflow Engine enums."""

from __future__ import annotations

from adip.workflow.enums import (
    ExecutionMode,
    RetryPolicy,
    TaskExecutionStatus,
    WorkflowStatus,
)


class TestWorkflowStatus:
    def test_values(self) -> None:
        assert WorkflowStatus.CREATED.value == "CREATED"
        assert WorkflowStatus.INITIALIZED.value == "INITIALIZED"
        assert WorkflowStatus.READY.value == "READY"
        assert WorkflowStatus.RUNNING.value == "RUNNING"
        assert WorkflowStatus.WAITING.value == "WAITING"
        assert WorkflowStatus.PAUSED.value == "PAUSED"
        assert WorkflowStatus.COMPLETED.value == "COMPLETED"
        assert WorkflowStatus.FAILED.value == "FAILED"
        assert WorkflowStatus.CANCELLED.value == "CANCELLED"

    def test_unique_values(self) -> None:
        values = [s.value for s in WorkflowStatus]
        assert len(values) == len(set(values))


class TestTaskExecutionStatus:
    def test_values(self) -> None:
        assert TaskExecutionStatus.PENDING.value == "PENDING"
        assert TaskExecutionStatus.READY.value == "READY"
        assert TaskExecutionStatus.RUNNING.value == "RUNNING"
        assert TaskExecutionStatus.WAITING.value == "WAITING"
        assert TaskExecutionStatus.COMPLETED.value == "COMPLETED"
        assert TaskExecutionStatus.FAILED.value == "FAILED"
        assert TaskExecutionStatus.CANCELLED.value == "CANCELLED"
        assert TaskExecutionStatus.RETRYING.value == "RETRYING"

    def test_unique_values(self) -> None:
        values = [s.value for s in TaskExecutionStatus]
        assert len(values) == len(set(values))


class TestExecutionMode:
    def test_values(self) -> None:
        assert ExecutionMode.SEQUENTIAL.value == "SEQUENTIAL"
        assert ExecutionMode.PARALLEL.value == "PARALLEL"
        assert ExecutionMode.CONDITIONAL.value == "CONDITIONAL"

    def test_unique_values(self) -> None:
        values = [s.value for s in ExecutionMode]
        assert len(values) == len(set(values))


class TestRetryPolicy:
    def test_values(self) -> None:
        assert RetryPolicy.NEVER.value == "NEVER"
        assert RetryPolicy.IMMEDIATE.value == "IMMEDIATE"
        assert RetryPolicy.EXPONENTIAL_BACKOFF.value == "EXPONENTIAL_BACKOFF"
        assert RetryPolicy.FIXED_DELAY.value == "FIXED_DELAY"

    def test_unique_values(self) -> None:
        values = [s.value for s in RetryPolicy]
        assert len(values) == len(set(values))
