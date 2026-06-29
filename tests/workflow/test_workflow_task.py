"""Validation tests for WorkflowTask and TaskResult."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from adip.workflow.contracts.models import TaskResult, WorkflowTask
from adip.workflow.enums import RetryPolicy, TaskExecutionStatus


class TestWorkflowTaskDefaults:
    def test_default_fields(self) -> None:
        task = WorkflowTask(task_id=uuid.uuid4(), task_name="Test")
        assert task.runtime_status == TaskExecutionStatus.PENDING
        assert task.assigned_executor is None
        assert task.inputs == {}
        assert task.outputs == {}
        assert task.dependencies == []
        assert task.retry_count == 0
        assert task.retry_policy == RetryPolicy.NEVER
        assert task.timeout is None
        assert task.execution_metadata == {}
        assert task.started_at is None
        assert task.completed_at is None

    def test_minimal_creation(self) -> None:
        task = WorkflowTask()
        assert task.task_name == ""
        assert task.description == ""
        assert task.runtime_status == TaskExecutionStatus.PENDING

    def test_uuid_auto_generated(self) -> None:
        t1 = WorkflowTask()
        t2 = WorkflowTask()
        assert t1.task_id != t2.task_id

    def test_retry_count_ge_zero(self) -> None:
        with pytest.raises(ValidationError):
            WorkflowTask(retry_count=-1)

    def test_timeout_ge_zero(self) -> None:
        WorkflowTask(timeout=0.0)
        WorkflowTask(timeout=10.0)
        with pytest.raises(ValidationError):
            WorkflowTask(timeout=-1.0)


class TestWorkflowTaskStatus:
    def test_default_status(self) -> None:
        task = WorkflowTask()
        assert task.runtime_status == TaskExecutionStatus.PENDING

    def test_custom_status(self) -> None:
        task = WorkflowTask(runtime_status=TaskExecutionStatus.READY)
        assert task.runtime_status == TaskExecutionStatus.READY

    def test_invalid_status_raises(self) -> None:
        with pytest.raises(ValidationError):
            WorkflowTask(runtime_status="INVALID")


class TestTaskResult:
    def test_default_fields(self) -> None:
        r = TaskResult()
        assert r.success is True
        assert r.outputs == {}
        assert r.execution_time is None
        assert r.warnings == []
        assert r.errors == []
        assert r.metadata == {}

    def test_failed_result(self) -> None:
        r = TaskResult(
            success=False,
            errors=["Connection refused"],
            execution_time=1.5,
        )
        assert r.success is False
        assert "Connection refused" in r.errors
        assert r.execution_time == 1.5

    def test_execution_time_ge_zero(self) -> None:
        TaskResult(execution_time=0.0)
        with pytest.raises(ValidationError):
            TaskResult(execution_time=-1.0)

    def test_custom_outputs(self) -> None:
        r = TaskResult(outputs={"result": 42, "status": "ok"})
        assert r.outputs["result"] == 42
