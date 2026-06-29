"""ResourceAllocator — personnel, equipment, inventory and budget allocation.

Allocates resources to action plan steps based on role requirements,
equipment needs, inventory consumption, and budget constraints
using deterministic placeholder logic.
"""

from __future__ import annotations

import structlog

from adip.actions.execution.models import ResourceAllocationResult

log = structlog.get_logger(__name__)


class ResourceAllocator:
    """Allocates personnel, equipment, inventory, and budget to steps."""

    def allocate_resources(
        self,
        plan_id: str = "",
        step_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> ResourceAllocationResult:
        """Allocate resources to steps.

        Args:
            plan_id: The plan ID.
            step_ids: List of step IDs to allocate resources to.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ResourceAllocationResult with allocated resources.
        """
        step_ids = step_ids or []

        personnel: dict[str, list[str]] = {}
        equipment: dict[str, list[str]] = {}
        inventory: dict[str, list[str]] = {}
        total_personnel = 0
        total_equipment = 0

        for i, sid in enumerate(step_ids):
            personnel[sid] = [f"engineer-{i + 1}", f"technician-{i + 1}"]
            equipment[sid] = [f"toolkit-{i + 1}", f"device-{i + 1}"]
            inventory[sid] = [f"part-{i + 1}"]
            total_personnel += len(personnel[sid])
            total_equipment += len(equipment[sid])

        budget = total_personnel * 100.0 + total_equipment * 50.0

        result = ResourceAllocationResult(
            plan_id=plan_id,
            personnel=personnel,
            equipment=equipment,
            inventory=inventory,
            budget=budget,
            total_personnel=total_personnel,
            total_equipment=total_equipment,
        )
        log.info(
            "resource_allocator.allocated",
            plan_id=plan_id,
            steps=len(step_ids),
            total_personnel=total_personnel,
            budget=budget,
            correlation_id=correlation_id,
        )
        return result

    def validate_resources(
        self,
        plan_id: str = "",
        step_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate resource allocations.

        Args:
            plan_id: The plan ID.
            step_ids: List of step IDs.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        violations: list[str] = []
        if not step_ids:
            violations.append("No steps to allocate resources to")
        return violations
