"""PortfolioComparator — compares recommendation portfolios.

Compares portfolios across cost, risk, ROI, business value,
and feasibility dimensions. Deterministic placeholder implementation.
"""

from __future__ import annotations

from typing import Any

import structlog

log = structlog.get_logger(__name__)


class PortfolioComparator:
    """Compares recommendation portfolios.

    Deterministic placeholder that compares portfolios across
    cost, risk, ROI, business value, and feasibility dimensions.
    """

    def compare(
        self,
        portfolio_a: dict[str, Any] | None = None,
        portfolio_b: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Compare two portfolios across key dimensions.

        Args:
            portfolio_a: First portfolio data.
            portfolio_b: Second portfolio data.

        Returns:
            Dictionary with comparison results across dimensions.
        """
        pa = portfolio_a or {}
        pb = portfolio_b or {}

        cost_a = pa.get("cost", 0.0)
        cost_b = pb.get("cost", 0.0)
        risk_a = pa.get("risk", 0.0)
        risk_b = pb.get("risk", 0.0)
        roi_a = pa.get("roi", 0.0)
        roi_b = pb.get("roi", 0.0)
        value_a = pa.get("business_value", 0.0)
        value_b = pb.get("business_value", 0.0)
        feasibility_a = pa.get("feasibility", 0.0)
        feasibility_b = pb.get("feasibility", 0.0)

        result = {
            "cost": {
                "a": cost_a,
                "b": cost_b,
                "difference": round(cost_a - cost_b, 2),
                "better": "a" if cost_a < cost_b else ("b" if cost_b < cost_a else "equal"),
            },
            "risk": {
                "a": risk_a,
                "b": risk_b,
                "difference": round(risk_a - risk_b, 4),
                "better": "a" if risk_a < risk_b else ("b" if risk_b < risk_a else "equal"),
            },
            "roi": {
                "a": roi_a,
                "b": roi_b,
                "difference": round(roi_a - roi_b, 2),
                "better": "a" if roi_a > roi_b else ("b" if roi_b > roi_a else "equal"),
            },
            "business_value": {
                "a": value_a,
                "b": value_b,
                "difference": round(value_a - value_b, 4),
                "better": "a" if value_a > value_b else ("b" if value_b > value_a else "equal"),
            },
            "feasibility": {
                "a": feasibility_a,
                "b": feasibility_b,
                "difference": round(feasibility_a - feasibility_b, 4),
                "better": "a" if feasibility_a > feasibility_b else ("b" if feasibility_b > feasibility_a else "equal"),
            },
        }

        scores = []
        if result["cost"]["better"] == "a":
            scores.append(1)
        elif result["cost"]["better"] == "b":
            scores.append(-1)
        else:
            scores.append(0)
        if result["risk"]["better"] == "a":
            scores.append(1)
        elif result["risk"]["better"] == "b":
            scores.append(-1)
        else:
            scores.append(0)
        if result["roi"]["better"] == "a":
            scores.append(1)
        elif result["roi"]["better"] == "b":
            scores.append(-1)
        else:
            scores.append(0)
        if result["business_value"]["better"] == "a":
            scores.append(1)
        elif result["business_value"]["better"] == "b":
            scores.append(-1)
        else:
            scores.append(0)
        if result["feasibility"]["better"] == "a":
            scores.append(1)
        elif result["feasibility"]["better"] == "b":
            scores.append(-1)
        else:
            scores.append(0)

        total = sum(scores)
        if total > 0:
            result["overall_recommendation"] = "portfolio_a"
        elif total < 0:
            result["overall_recommendation"] = "portfolio_b"
        else:
            result["overall_recommendation"] = "equal"

        log.info("portfolio.compare", overall=result["overall_recommendation"])
        return result

    def compare_portfolios(
        self,
        portfolio_a,
        portfolio_b,
    ) -> dict[str, Any]:
        """Compare two portfolio objects.

        Args:
            portfolio_a: First portfolio object.
            portfolio_b: Second portfolio object.

        Returns:
            Comparison result dict.
        """
        pa = {}
        pb = {}
        if portfolio_a:
            pa = {
                "cost": getattr(portfolio_a, 'cost', 0.0) if hasattr(portfolio_a, 'cost') else 0.0,
                "risk": getattr(portfolio_a, 'risk', 0.0) if hasattr(portfolio_a, 'risk') else 0.0,
                "roi": 0.0,
                "business_value": getattr(portfolio_a, 'overall_confidence', 0.0),
                "feasibility": getattr(portfolio_a, 'overall_confidence', 0.0) * 0.8,
            }
        if portfolio_b:
            pb = {
                "cost": getattr(portfolio_b, 'cost', 0.0) if hasattr(portfolio_b, 'cost') else 0.0,
                "risk": getattr(portfolio_b, 'risk', 0.0) if hasattr(portfolio_b, 'risk') else 0.0,
                "roi": 0.0,
                "business_value": getattr(portfolio_b, 'overall_confidence', 0.0),
                "feasibility": getattr(portfolio_b, 'overall_confidence', 0.0) * 0.8,
            }
        return self.compare(portfolio_a=pa, portfolio_b=pb)
