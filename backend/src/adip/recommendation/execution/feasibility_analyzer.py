"""FeasibilityAnalyzer — evaluates recommendation feasibility.

Evaluates whether recommendation candidates are feasible based on
resources, budget, inventory, technician availability, time windows,
and operational constraints.
Deterministic placeholder implementation.
"""

from __future__ import annotations

import structlog

from adip.recommendation.enums import FeasibilityStatus
from adip.recommendation.execution.models import FeasibilityAnalysis

log = structlog.get_logger(__name__)


class FeasibilityAnalyzer:
    """Evaluates feasibility of recommendation candidates.

    Deterministic placeholder that checks resource, budget, inventory,
    technician, time window, and operational feasibility.
    """

    def analyze(
        self,
        resource_score: float = 0.5,
        budget_score: float = 0.5,
        inventory_score: float = 0.5,
        technician_score: float = 0.5,
        time_window_score: float = 0.5,
        operational_score: float = 0.5,
        constraints: list[str] | None = None,
    ) -> FeasibilityAnalysis:
        """Analyze the feasibility of a recommendation.

        Args:
            resource_score: Resource availability score (0.0–1.0).
            budget_score: Budget availability score (0.0–1.0).
            inventory_score: Inventory availability score (0.0–1.0).
            technician_score: Technician availability score (0.0–1.0).
            time_window_score: Time window availability score (0.0–1.0).
            operational_score: Operational feasibility score (0.0–1.0).
            constraints: Optional list of identified constraints.

        Returns:
            FeasibilityAnalysis with detailed assessment.
        """
        constraints = constraints or []
        resources_available = resource_score >= 0.5
        budget_available = budget_score >= 0.5
        inventory_available = inventory_score >= 0.5
        technician_available = technician_score >= 0.5
        time_window_available = time_window_score >= 0.5
        operational_feasible = operational_score >= 0.5

        feasibility_score = round(
            (max(0.0, min(1.0, resource_score)) * 0.2
             + max(0.0, min(1.0, budget_score)) * 0.2
             + max(0.0, min(1.0, inventory_score)) * 0.15
             + max(0.0, min(1.0, technician_score)) * 0.15
             + max(0.0, min(1.0, time_window_score)) * 0.15
             + max(0.0, min(1.0, operational_score)) * 0.15),
            4,
        )

        status = FeasibilityStatus.FEASIBLE if feasibility_score >= 0.7 else (
            FeasibilityStatus.PARTIALLY_FEASIBLE if feasibility_score >= 0.4
            else FeasibilityStatus.NOT_FEASIBLE
        )

        log.info("feasibility_analyzer.analyze", status=status.value, score=feasibility_score)
        return FeasibilityAnalysis(
            status=status,
            resources_available=resources_available,
            budget_available=budget_available,
            inventory_available=inventory_available,
            technician_available=technician_available,
            time_window_available=time_window_available,
            operational_feasible=operational_feasible,
            feasibility_score=feasibility_score,
            constraints=constraints,
        )

    def analyze_candidate(
        self,
        candidate,
        domain: str = "",
    ) -> FeasibilityAnalysis:
        """Analyze feasibility for a specific candidate.

        Args:
            candidate: The recommendation candidate (with estimated_cost field).
            domain: Optional domain string.

        Returns:
            FeasibilityAnalysis.
        """
        cost = getattr(candidate, "estimated_cost", 5000.0)
        budget_ok = cost < 10000.0
        return self.analyze(
            resource_score=0.7,
            budget_score=0.8 if budget_ok else 0.3,
            inventory_score=0.6,
            technician_score=0.7,
            time_window_score=0.5,
            operational_score=0.6,
            constraints=[],
        )
