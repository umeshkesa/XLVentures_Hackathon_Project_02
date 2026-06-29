"""ActionRiskEvaluator — operational, safety, financial, compliance and execution risk evaluation.

Evaluates five dimensions of risk for action plans using
deterministic placeholder heuristics based on action type,
priority, step count, and target domain.
"""

from __future__ import annotations

import structlog

from adip.actions.execution.models import RiskEvaluation

log = structlog.get_logger(__name__)


class ActionRiskEvaluator:
    """Evaluates operational, safety, financial, compliance, and execution risk."""

    RISK_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

    def evaluate(
        self,
        plan_id: str = "",
        action_type: str = "AUTOMATED",
        priority: str = "MEDIUM",
        step_count: int = 0,
        domain: str = "",
        correlation_id: str = "",
    ) -> RiskEvaluation:
        """Evaluate risk across all five dimensions.

        Uses deterministic heuristics:
        - Emergency action type → CRITICAL for all dimensions
        - Manual/WORKFLOW → higher operational/execution risk
        - HIGH/CRITICAL priority → higher financial/execution risk
        - More steps → higher execution risk
        - SAFETY domain → higher safety risk
        - COMPLIANCE domain → higher compliance risk

        Args:
            plan_id: The plan ID.
            action_type: The action type string.
            priority: The priority string.
            step_count: Number of steps.
            domain: The domain string.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            RiskEvaluation with per-dimension and overall risk.
        """
        at = action_type.upper() if action_type else "AUTOMATED"
        pri = priority.upper() if priority else "MEDIUM"
        dom = domain.upper() if domain else ""

        operational = self._evaluate_operational(at, pri, step_count)
        safety = self._evaluate_safety(at, dom)
        financial = self._evaluate_financial(at, pri, step_count)
        compliance = self._evaluate_compliance(at, dom)
        execution = self._evaluate_execution(at, pri, step_count)
        overall = self._aggregate([operational, safety, financial, compliance, execution])

        risk_factors = self._identify_factors(at, pri, dom, step_count)

        result = RiskEvaluation(
            plan_id=plan_id,
            operational_risk=operational,
            safety_risk=safety,
            financial_risk=financial,
            compliance_risk=compliance,
            execution_risk=execution,
            overall_risk=overall,
            risk_factors=risk_factors,
        )
        log.info(
            "risk_evaluator.evaluated",
            plan_id=plan_id,
            overall_risk=overall,
            correlation_id=correlation_id,
        )
        return result

    def _evaluate_operational(self, action_type: str, priority: str, step_count: int) -> str:
        if action_type == "EMERGENCY":
            return "CRITICAL"
        if action_type in ("MANUAL", "WORKFLOW"):
            return "HIGH"
        if priority == "CRITICAL":
            return "HIGH"
        if step_count > 5:
            return "MEDIUM"
        return "LOW"

    def _evaluate_safety(self, action_type: str, domain: str) -> str:
        if action_type == "EMERGENCY":
            return "CRITICAL"
        if domain in ("SAFETY", "ENERGY"):
            return "HIGH"
        if action_type == "MANUAL":
            return "MEDIUM"
        return "LOW"

    def _evaluate_financial(self, action_type: str, priority: str, step_count: int) -> str:
        if action_type == "EMERGENCY":
            return "CRITICAL"
        if priority in ("CRITICAL", "HIGH"):
            return "HIGH"
        if step_count > 10:
            return "MEDIUM"
        return "LOW"

    def _evaluate_compliance(self, action_type: str, domain: str) -> str:
        if domain == "COMPLIANCE":
            return "HIGH"
        if action_type == "EXTERNAL_INTEGRATION":
            return "MEDIUM"
        return "LOW"

    def _evaluate_execution(self, action_type: str, priority: str, step_count: int) -> str:
        if action_type == "EMERGENCY":
            return "CRITICAL"
        if step_count > 8:
            return "HIGH"
        if step_count > 4:
            return "MEDIUM"
        return "LOW"

    def _aggregate(self, risks: list[str]) -> str:
        """Aggregate multiple risk levels into overall."""
        levels = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
        max_level = max(levels.get(r, 0) for r in risks)
        reverse_map = {0: "LOW", 1: "MEDIUM", 2: "HIGH", 3: "CRITICAL"}
        return reverse_map.get(max_level, "LOW")

    def _identify_factors(
        self,
        action_type: str,
        priority: str,
        domain: str,
        step_count: int,
    ) -> list[str]:
        factors = []
        if action_type == "EMERGENCY":
            factors.append("Emergency action carries inherent high risk")
        if priority in ("CRITICAL", "HIGH"):
            factors.append("High priority increases execution pressure")
        if domain in ("SAFETY", "ENERGY"):
            factors.append(f"{domain} domain requires specialised risk assessment")
        if step_count > 8:
            factors.append("Large number of steps increases execution complexity")
        return factors
