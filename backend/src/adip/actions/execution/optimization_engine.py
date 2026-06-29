"""ActionOptimizationEngine — cost, duration, resource, safety and downtime optimization.

Optimises action plans across five dimensions: cost, duration,
resource utilisation, safety, and downtime, returning an
OptimizationResult with pre- and post-optimisation metrics.
"""

from __future__ import annotations

import structlog

from adip.actions.execution.models import CostEstimate, CriticalPath, OptimizationResult

log = structlog.get_logger(__name__)


class ActionOptimizationEngine:
    """Optimises action plans for cost, duration, resource utilisation, safety, and downtime."""

    def optimize(
        self,
        plan_id: str = "",
        cost_estimate: CostEstimate | None = None,
        critical_path: CriticalPath | None = None,
        step_count: int = 0,
        correlation_id: str = "",
    ) -> OptimizationResult:
        """Optimise an action plan across all dimensions.

        Uses deterministic placeholder optimisation logic:
        - Cost: 15% reduction through resource consolidation
        - Duration: 20% reduction through parallelisation
        - Resource utilisation: 25% improvement through load balancing
        - Safety: 10% improvement through additional checks
        - Downtime: 30% reduction through scheduling optimisation

        Args:
            plan_id: The plan ID.
            cost_estimate: The current cost estimate.
            critical_path: The critical path analysis result.
            step_count: Number of steps.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            OptimizationResult with original/optimised values.
        """
        cost = cost_estimate or CostEstimate(plan_id=plan_id)
        path = critical_path or CriticalPath(plan_id=plan_id)

        original_cost = cost.total_cost
        original_duration = path.total_duration_minutes
        original_utilization = 0.5  # placeholder
        original_safety = 0.7  # placeholder
        original_downtime = cost.downtime_cost

        optimized_cost = original_cost * 0.85
        optimized_duration = max(1, int(original_duration * 0.8))
        optimized_utilization = min(1.0, original_utilization * 1.25)
        optimized_safety = min(1.0, original_safety * 1.1)
        optimized_downtime = original_downtime * 0.7

        cost_savings = original_cost - optimized_cost
        duration_reduction = max(0, original_duration - optimized_duration)

        improvements = []
        if cost_savings > 0:
            improvements.append(f"Cost reduced by {cost_savings:.2f}")
        if duration_reduction > 0:
            improvements.append(f"Duration reduced by {duration_reduction} minutes")
        if optimized_utilization > original_utilization:
            improvements.append("Resource utilisation improved")
        if optimized_safety > original_safety:
            improvements.append("Safety score improved")
        if optimized_downtime < original_downtime:
            improvements.append("Downtime reduced")

        # Overall optimization score (0-1) based on improvements
        score_dims = [
            (original_cost - optimized_cost) / max(original_cost, 1),
            (original_duration - optimized_duration) / max(original_duration, 1),
            (optimized_utilization - original_utilization) / max(original_utilization, 0.01),
            (optimized_safety - original_safety),
            (original_downtime - optimized_downtime) / max(original_downtime, 1),
        ]
        avg_improvement = sum(max(0, d) for d in score_dims) / len(score_dims)
        optimization_score = min(1.0, max(0.0, 0.5 + avg_improvement * 0.5))

        result = OptimizationResult(
            plan_id=plan_id,
            original_cost=original_cost,
            optimized_cost=optimized_cost,
            original_duration_minutes=original_duration,
            optimized_duration_minutes=optimized_duration,
            original_resource_utilization=original_utilization,
            optimized_resource_utilization=optimized_utilization,
            original_safety_score=original_safety,
            optimized_safety_score=optimized_safety,
            original_downtime_minutes=int(original_downtime),
            optimized_downtime_minutes=int(optimized_downtime),
            cost_savings=cost_savings,
            duration_reduction_minutes=duration_reduction,
            optimization_score=round(optimization_score, 4),
            improvements=improvements,
        )
        log.info(
            "optimization_engine.optimized",
            plan_id=plan_id,
            score=optimization_score,
            improvements=len(improvements),
            correlation_id=correlation_id,
        )
        return result
