"""CostAnalyzer — estimates recommendation costs.

Estimates implementation, operational, and downtime costs,
plus ROI for recommendation candidates.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.recommendation.execution.models import CostEstimate

log = structlog.get_logger(__name__)


class CostAnalyzer:
    """Estimates costs for recommendation candidates.

    Deterministic placeholder that estimates implementation,
    operational, and downtime costs plus ROI.
    """

    def estimate(
        self,
        implementation_cost: float = 1000.0,
        operational_cost: float = 500.0,
        downtime_cost: float = 0.0,
        expected_benefit: float = 5000.0,
        currency: str = "USD",
    ) -> CostEstimate:
        """Estimate costs for a recommendation.

        Args:
            implementation_cost: Estimated implementation cost.
            operational_cost: Estimated ongoing operational cost.
            downtime_cost: Estimated cost of downtime during implementation.
            expected_benefit: Expected benefit from the recommendation.
            currency: Currency code.

        Returns:
            CostEstimate with all cost components.
        """
        ic = max(0.0, implementation_cost)
        oc = max(0.0, operational_cost)
        dc = max(0.0, downtime_cost)
        total = ic + oc + dc
        eb = max(0.0, expected_benefit)
        roi = round(((eb - total) / total * 100), 2) if total > 0 else 0.0
        log.info("cost_analyzer.estimate", total=total, roi=roi, currency=currency)
        return CostEstimate(
            implementation_cost=ic,
            operational_cost=oc,
            downtime_cost=dc,
            total_cost=total,
            roi=roi,
            currency=currency,
        )

    def estimate_candidate(
        self,
        candidate,
        multiplier: float = 1.0,
    ) -> CostEstimate:
        """Estimate costs for a specific candidate.

        Args:
            candidate: The recommendation candidate.
            multiplier: Multiplier for cost estimation.

        Returns:
            CostEstimate.
        """
        base_cost = getattr(candidate, "estimated_cost", 5000.0)
        return self.estimate(
            implementation_cost=base_cost * multiplier,
            operational_cost=base_cost * 0.3 * multiplier,
            downtime_cost=base_cost * 0.1 * multiplier,
            expected_benefit=base_cost * 3.0 * multiplier,
        )
