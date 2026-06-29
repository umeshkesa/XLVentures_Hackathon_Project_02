"""ActionPlanner — placeholder action plan generation.

Generates placeholder ActionPlans based on action type,
decomposing an approved action into ordered steps with
preconfigured parameters for each action type.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import structlog

from adip.actions.contracts.models import ActionPlan, ActionPlanStep, ActionRequest
from adip.actions.enums import ActionPriority, ActionType

log = structlog.get_logger(__name__)


class ActionPlanner:
    """Generates placeholder ActionPlans from ActionRequests."""

    def generate_plan(
        self,
        request: ActionRequest,
        correlation_id: str = "",
    ) -> ActionPlan:
        """Generate a placeholder ActionPlan based on the request.

        Args:
            request: The action request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A generated ActionPlan with steps based on action type.
        """
        plan_id = uuid.uuid4()
        steps = self._generate_steps(request, plan_id)
        plan = ActionPlan(
            plan_id=plan_id,
            request_id=request.request_id,
            review_decision_id=request.review_decision_id,
            name=f"Plan - {request.action_type.value}",
            description=f"Auto-generated plan for {request.action_type.value} action",
            steps=steps,
            is_primary=True,
            status="DRAFT",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        log.info(
            "action_planner.plan_generated",
            plan_id=str(plan_id),
            action_type=request.action_type.value,
            step_count=len(steps),
            correlation_id=correlation_id,
        )
        return plan

    def _generate_steps(
        self,
        request: ActionRequest,
        plan_id: uuid.UUID4,
    ) -> list[ActionPlanStep]:
        """Generate steps for the given action type."""
        generators = {
            ActionType.MANUAL: self._manual_steps,
            ActionType.AUTOMATED: self._automated_steps,
            ActionType.APPROVAL: self._approval_steps,
            ActionType.NOTIFICATION: self._notification_steps,
            ActionType.WORKFLOW: self._workflow_steps,
            ActionType.EXTERNAL_INTEGRATION: self._external_steps,
            ActionType.EMERGENCY: self._emergency_steps,
        }
        generator = generators.get(request.action_type, self._automated_steps)
        return generator(request, plan_id)

    def _manual_steps(
        self,
        request: ActionRequest,
        plan_id: uuid.UUID4,
    ) -> list[ActionPlanStep]:
        return [
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.MANUAL,
                name="Assign operator",
                description="Assign qualified operator to perform action",
                priority=request.priority,
                order=0,
                parameters={"operator_role": "technician", "count": 1},
                timeout_seconds=600,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.MANUAL,
                name="Verify safety conditions",
                description="Confirm safety conditions are met before proceeding",
                priority=ActionPriority.CRITICAL,
                order=1,
                parameters={"safety_checklist": ["lockout", "tagout", "ppe"]},
                timeout_seconds=300,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.MANUAL,
                name="Execute manual action",
                description="Operator performs the required manual action",
                priority=request.priority,
                order=2,
                parameters={"target": request.target},
                timeout_seconds=3600,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.MANUAL,
                name="Confirm completion",
                description="Verify action completed successfully",
                priority=request.priority,
                order=3,
                parameters={"verification_required": True},
                timeout_seconds=300,
            ),
        ]

    def _automated_steps(
        self,
        request: ActionRequest,
        plan_id: uuid.UUID4,
    ) -> list[ActionPlanStep]:
        return [
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.AUTOMATED,
                name="Validate preconditions",
                description="Validate system preconditions for automated action",
                priority=ActionPriority.CRITICAL,
                order=0,
                parameters={"precondition_check": True},
                timeout_seconds=60,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.AUTOMATED,
                name="Execute automated action",
                description="System executes the automated action",
                priority=request.priority,
                order=1,
                parameters={"target": request.target},
                timeout_seconds=600,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.AUTOMATED,
                name="Verify outcome",
                description="Verify automated action completed successfully",
                priority=request.priority,
                order=2,
                parameters={"verification_timeout": 120},
                timeout_seconds=120,
            ),
        ]

    def _approval_steps(
        self,
        request: ActionRequest,
        plan_id: uuid.UUID4,
    ) -> list[ActionPlanStep]:
        return [
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.APPROVAL,
                name="Submit approval request",
                description="Submit action for approval",
                priority=request.priority,
                order=0,
                parameters={"approval_workflow": "standard"},
                timeout_seconds=86400,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.APPROVAL,
                name="Wait for approval decision",
                description="Await approval decision from authorized reviewer",
                priority=request.priority,
                order=1,
                parameters={"notify_on_approval": True},
                timeout_seconds=86400,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.AUTOMATED,
                name="Execute approved action",
                description="Execute the action after approval",
                priority=request.priority,
                order=2,
                parameters={"target": request.target},
                timeout_seconds=600,
            ),
        ]

    def _notification_steps(
        self,
        request: ActionRequest,
        plan_id: uuid.UUID4,
    ) -> list[ActionPlanStep]:
        return [
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.NOTIFICATION,
                name="Prepare notification",
                description="Prepare notification content",
                priority=request.priority,
                order=0,
                parameters={"channels": ["email", "dashboard"]},
                timeout_seconds=60,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.NOTIFICATION,
                name="Send notification",
                description="Send notification to stakeholders",
                priority=request.priority,
                order=1,
                parameters={"target_audience": "all_stakeholders"},
                timeout_seconds=60,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.NOTIFICATION,
                name="Confirm delivery",
                description="Confirm notification delivery",
                priority=request.priority,
                order=2,
                parameters={"confirmation_required": True},
                timeout_seconds=120,
            ),
        ]

    def _workflow_steps(
        self,
        request: ActionRequest,
        plan_id: uuid.UUID4,
    ) -> list[ActionPlanStep]:
        return [
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.WORKFLOW,
                name="Initialize workflow",
                description="Initialize multi-step workflow",
                priority=request.priority,
                order=0,
                parameters={"workflow_definition": "standard"},
                timeout_seconds=300,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.WORKFLOW,
                name="Execute workflow step 1",
                description="Execute first workflow step",
                priority=request.priority,
                order=1,
                parameters={"step_name": "validate", "target": request.target},
                timeout_seconds=600,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.WORKFLOW,
                name="Execute workflow step 2",
                description="Execute second workflow step",
                priority=request.priority,
                order=2,
                parameters={"step_name": "process", "target": request.target},
                timeout_seconds=600,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.WORKFLOW,
                name="Execute workflow step 3",
                description="Execute third workflow step",
                priority=request.priority,
                order=3,
                parameters={"step_name": "finalize", "target": request.target},
                timeout_seconds=600,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.WORKFLOW,
                name="Complete workflow",
                description="Finalize and complete workflow",
                priority=request.priority,
                order=4,
                parameters={"workflow_complete": True},
                timeout_seconds=120,
            ),
        ]

    def _external_steps(
        self,
        request: ActionRequest,
        plan_id: uuid.UUID4,
    ) -> list[ActionPlanStep]:
        return [
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.EXTERNAL_INTEGRATION,
                name="Authenticate with external system",
                description="Authenticate with external integration target",
                priority=ActionPriority.CRITICAL,
                order=0,
                parameters={"auth_method": "oauth2"},
                timeout_seconds=120,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.EXTERNAL_INTEGRATION,
                name="Prepare external request",
                description="Prepare payload for external system",
                priority=request.priority,
                order=1,
                parameters={"target": request.target},
                timeout_seconds=60,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.EXTERNAL_INTEGRATION,
                name="Send external request",
                description="Send request to external system",
                priority=request.priority,
                order=2,
                parameters={"timeout_seconds": 300},
                timeout_seconds=300,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.EXTERNAL_INTEGRATION,
                name="Process external response",
                description="Process response from external system",
                priority=request.priority,
                order=3,
                parameters={"validate_response": True},
                timeout_seconds=60,
            ),
        ]

    def _emergency_steps(
        self,
        request: ActionRequest,
        plan_id: uuid.UUID4,
    ) -> list[ActionPlanStep]:
        return [
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.EMERGENCY,
                name="Trigger emergency protocol",
                description="Trigger emergency action protocol",
                priority=ActionPriority.CRITICAL,
                order=0,
                parameters={"protocol": "emergency_override"},
                timeout_seconds=30,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.EMERGENCY,
                name="Execute emergency action",
                description="Execute emergency action immediately",
                priority=ActionPriority.CRITICAL,
                order=1,
                parameters={"target": request.target, "emergency_mode": True},
                timeout_seconds=120,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.EMERGENCY,
                name="Verify emergency outcome",
                description="Verify emergency action was executed",
                priority=ActionPriority.CRITICAL,
                order=2,
                parameters={"verification_required": True},
                timeout_seconds=60,
            ),
            ActionPlanStep(
                plan_id=plan_id,
                action_type=ActionType.NOTIFICATION,
                name="Notify stakeholders",
                description="Notify stakeholders of emergency action",
                priority=ActionPriority.CRITICAL,
                order=3,
                parameters={"channels": ["all"]},
                timeout_seconds=30,
            ),
        ]

    def validate_plan(
        self,
        plan: ActionPlan,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate an action plan.

        Args:
            plan: The action plan to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        violations: list[str] = []
        if not plan.steps:
            violations.append("Plan must have at least one step")
        if not plan.name:
            violations.append("Plan must have a name")
        step_ids = [str(s.step_id) for s in plan.steps]
        if len(step_ids) != len(set(step_ids)):
            violations.append("Duplicate step IDs detected")
        return violations
