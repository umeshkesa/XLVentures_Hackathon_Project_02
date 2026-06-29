"""Validation tests for WorkflowResult and WorkflowMetrics."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from adip.workflow.contracts.models import (
    TaskResult,
    WorkflowMetrics,
    WorkflowResult,
)
from adip.workflow.enums import WorkflowStatus


class TestWorkflowResult:
    def test_default_fields(self) -> None:
        r = WorkflowResult(workflow_id=uuid.uuid4())
        assert r.workflow_status == WorkflowStatus.CREATED
        assert r.completed_tasks == 0
        assert r.failed_tasks == 0
        assert r.skipped_tasks == 0
        assert r.execution_time == 0.0
        assert r.execution_summary == ""
        assert r.task_results == {}
        assert r.events == []

    def test_custom_status(self) -> None:
        r = WorkflowResult(
            workflow_id=uuid.uuid4(),
            workflow_status=WorkflowStatus.COMPLETED,
            completed_tasks=5,
            execution_time=1200.0,
            execution_summary="All tasks succeeded",
        )
        assert r.workflow_status == WorkflowStatus.COMPLETED
        assert r.completed_tasks == 5
        assert r.execution_time == 1200.0
        assert "succeeded" in r.execution_summary

    def test_task_results(self) -> None:
        tid = uuid.uuid4()
        r = WorkflowResult(
            workflow_id=uuid.uuid4(),
            task_results={tid: TaskResult(success=True)},
        )
        assert r.task_results[tid].success is True

    def test_counters_ge_zero(self) -> None:
        r = WorkflowResult(
            workflow_id=uuid.uuid4(),
            completed_tasks=0,
            failed_tasks=0,
            skipped_tasks=0,
        )
        assert r.completed_tasks >= 0
        with pytest.raises(ValidationError):
            WorkflowResult(workflow_id=uuid.uuid4(), completed_tasks=-1)
        with pytest.raises(ValidationError):
            WorkflowResult(workflow_id=uuid.uuid4(), failed_tasks=-1)
        with pytest.raises(ValidationError):
            WorkflowResult(workflow_id=uuid.uuid4(), skipped_tasks=-1)

    def test_execution_time_ge_zero(self) -> None:
        with pytest.raises(ValidationError):
            WorkflowResult(workflow_id=uuid.uuid4(), execution_time=-0.1)


class TestWorkflowMetrics:
    def test_default_fields(self) -> None:
        m = WorkflowMetrics()
        assert m.total_execution_time == 0.0
        assert m.successful_tasks == 0
        assert m.failed_tasks == 0
        assert m.retry_count == 0
        assert m.waiting_time == 0.0
        assert m.parallel_execution_percentage == 0.0
        assert m.resource_usage == {}
        assert m.approval_wait_time == 0.0

    def test_custom_metrics(self) -> None:
        m = WorkflowMetrics(
            total_execution_time=1500.0,
            successful_tasks=10,
            failed_tasks=2,
            retry_count=3,
            parallel_execution_percentage=75.0,
        )
        assert m.total_execution_time == 1500.0
        assert m.parallel_execution_percentage == 75.0

    def test_parallel_percentage_bounds(self) -> None:
        WorkflowMetrics(parallel_execution_percentage=0.0)
        WorkflowMetrics(parallel_execution_percentage=100.0)
        with pytest.raises(ValidationError):
            WorkflowMetrics(parallel_execution_percentage=-0.1)
        with pytest.raises(ValidationError):
            WorkflowMetrics(parallel_execution_percentage=100.1)

    def test_counters_ge_zero(self) -> None:
        with pytest.raises(ValidationError):
            WorkflowMetrics(successful_tasks=-1)
        with pytest.raises(ValidationError):
            WorkflowMetrics(failed_tasks=-1)
        with pytest.raises(ValidationError):
            WorkflowMetrics(retry_count=-1)
