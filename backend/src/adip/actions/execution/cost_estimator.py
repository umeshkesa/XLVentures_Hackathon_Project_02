"""ActionCostEstimator — labour, equipment, downtime, materials and external cost estimation.

Estimates costs for action plans across five dimensions:
labour, equipment, downtime, materials, and external services,
providing a total cost breakdown.
"""

from __future__ import annotations

import structlog

from adip.actions.execution.models import CostEstimate

log = structlog.get_logger(__name__)


class ActionCostEstimator:
    """Estimates labour, equipment, downtime, materials, and external costs."""

    def estimate_costs(
        self,
        plan_id: str = "",
        step_count: int = 0,
        step_ids: list[str] | None = None,
        correlation_id: str = "",
    ) -> CostEstimate:
        """Estimate costs for an action plan.

        Uses deterministic placeholder formulas based on step count:
        - Labour: step_count * 2 personnel * $50/hr * 2 hours
        - Equipment: step_count * $200
        - Downtime: step_count * $500
        - Materials: step_count * $150
        - External: step_count * $100

        Args:
            plan_id: The plan ID.
            step_count: Number of steps in the plan.
            step_ids: Optional list of step IDs.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            CostEstimate with per-dimension and total costs.
        """
        n = max(step_count, len(step_ids or []))
        labour = n * 2.0 * 50.0 * 2.0
        equipment = n * 200.0
        downtime = n * 500.0
        materials = n * 150.0
        external = n * 100.0
        total = labour + equipment + downtime + materials + external

        estimate = CostEstimate(
            plan_id=plan_id,
            labor_cost=labour,
            equipment_cost=equipment,
            downtime_cost=downtime,
            materials_cost=materials,
            external_services_cost=external,
            total_cost=total,
            currency="USD",
        )
        log.info(
            "cost_estimator.estimated",
            plan_id=plan_id,
            total_cost=total,
            step_count=n,
            correlation_id=correlation_id,
        )
        return estimate

    def estimate_step_cost(
        self,
        step_id: str = "",
        step_type: str = "automated",
    ) -> float:
        """Estimate the cost of a single step by type.

        Returns:
            Estimated cost for the step.
        """
        base_costs = {
            "manual": 500.0,
            "automated": 100.0,
            "approval": 50.0,
            "notification": 20.0,
            "workflow": 300.0,
            "external_integration": 400.0,
            "emergency": 1000.0,
        }
        return base_costs.get(step_type, 100.0)

    def get_cost_breakdown(
        self,
        estimate: CostEstimate,
    ) -> dict[str, float]:
        """Get a named breakdown of cost components."""
        return {
            "labor": estimate.labor_cost,
            "equipment": estimate.equipment_cost,
            "downtime": estimate.downtime_cost,
            "materials": estimate.materials_cost,
            "external_services": estimate.external_services_cost,
        }
