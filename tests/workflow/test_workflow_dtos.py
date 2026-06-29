"""Validation tests for Workflow DTOs."""

from __future__ import annotations

from adip.planner.contracts.models import ExecutionPlan, PlanningGoal
from adip.workflow.contracts.models import WorkflowContext
from adip.workflow.enums import WorkflowStatus
from adip.workflow.services.dtos import (
    WorkflowRequestDTO,
    WorkflowResponseDTO,
)


class TestWorkflowRequestDTO:
    def test_minimal_creation(self) -> None:
        plan = ExecutionPlan(
            goal=PlanningGoal(objective="Test workflow"),
        )
        dto = WorkflowRequestDTO(execution_plan=plan)
        assert dto.execution_plan.goal.objective == "Test workflow"
        assert dto.workflow_context is not None

    def test_custom_context(self) -> None:
        plan = ExecutionPlan(goal=PlanningGoal(objective="Test"))
        ctx = WorkflowContext(
            user_context={"user_id": "abc123"},
            environment_context={"env": "production"},
        )
        dto = WorkflowRequestDTO(
            execution_plan=plan,
            workflow_context=ctx,
            metadata={"source": "api"},
        )
        assert dto.workflow_context.user_context["user_id"] == "abc123"
        assert dto.metadata["source"] == "api"


class TestWorkflowResponseDTO:
    def test_default_creation(self) -> None:
        import uuid
        dto = WorkflowResponseDTO(workflow_id=uuid.uuid4())
        assert dto.workflow_status == WorkflowStatus.CREATED
        assert dto.completed_tasks == 0
        assert dto.events == []

    def test_custom_status(self) -> None:
        import uuid
        dto = WorkflowResponseDTO(
            workflow_id=uuid.uuid4(),
            workflow_status=WorkflowStatus.COMPLETED,
            execution_summary="Success",
            execution_time=500.0,
        )
        assert dto.workflow_status == WorkflowStatus.COMPLETED
        assert "Success" in dto.execution_summary
