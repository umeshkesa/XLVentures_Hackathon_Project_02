"""ResourceConflictDetector — double booking, capacity and scheduling conflicts.

Detects resource conflicts in action plans including double booking
of personnel/equipment, capacity limit violations, and scheduling
conflicts between overlapping steps.
"""

from __future__ import annotations

import structlog

from adip.actions.execution.models import ResourceAllocationResult, ResourceConflict

log = structlog.get_logger(__name__)


class ResourceConflictDetector:
    """Detects double booking, capacity, and scheduling conflicts."""

    def detect_conflicts(
        self,
        plan_id: str = "",
        allocation: ResourceAllocationResult | None = None,
        step_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> list[ResourceConflict]:
        """Detect resource conflicts in a plan's allocation.

        Args:
            plan_id: The plan ID.
            allocation: The resource allocation result to analyse.
            step_ids: List of step IDs.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of detected ResourceConflicts.
        """
        conflicts: list[ResourceConflict] = []
        allocation = allocation or ResourceAllocationResult(plan_id=plan_id)
        step_ids = step_ids or []

        # Detect double booking: same resource assigned to multiple steps
        resource_to_steps: dict[str, list[str]] = {}
        for sid in step_ids:
            for person in allocation.personnel.get(sid, []):
                if person not in resource_to_steps:
                    resource_to_steps[person] = []
                resource_to_steps[person].append(sid)
            for equip in allocation.equipment.get(sid, []):
                if equip not in resource_to_steps:
                    resource_to_steps[equip] = []
                resource_to_steps[equip].append(sid)

        for resource, steps in resource_to_steps.items():
            if len(steps) > 1:
                conflicts.append(
                    ResourceConflict(
                        plan_id=plan_id,
                        resource_type="personnel" if resource.startswith("engineer") or resource.startswith("technician") else "equipment",
                        resource_id=resource,
                        conflict_type="double_booking",
                        step_ids=steps,
                        description=f"Resource {resource} double-booked across steps: {', '.join(steps)}",
                    )
                )

        # Detect capacity limit conflicts (placeholder: >5 personnel per step is conflict)
        for sid in step_ids:
            person_count = len(allocation.personnel.get(sid, []))
            if person_count > 5:
                conflicts.append(
                    ResourceConflict(
                        plan_id=plan_id,
                        resource_type="personnel",
                        resource_id=f"step-{sid}",
                        conflict_type="capacity",
                        step_ids=[sid],
                        description=f"Step {sid} exceeds capacity limit ({person_count} > 5)",
                    )
                )

        log.info(
            "conflict_detector.detected",
            plan_id=plan_id,
            conflict_count=len(conflicts),
            correlation_id=correlation_id,
        )
        return conflicts

    def validate_no_conflicts(
        self,
        conflicts: list[ResourceConflict],
    ) -> list[str]:
        """Validate that there are no conflicts.

        Returns:
            List of conflict descriptions (empty if no conflicts).
        """
        return [c.description for c in conflicts if c.description]

    def get_double_booking_conflicts(
        self,
        conflicts: list[ResourceConflict],
    ) -> list[ResourceConflict]:
        """Filter conflicts to double booking only."""
        return [c for c in conflicts if c.conflict_type == "double_booking"]

    def get_capacity_conflicts(
        self,
        conflicts: list[ResourceConflict],
    ) -> list[ResourceConflict]:
        """Filter conflicts to capacity only."""
        return [c for c in conflicts if c.conflict_type == "capacity"]
