"""Planner service adapter — enterprise agent orchestration visualization."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from adip.api.rest.adapters.base import BaseServiceAdapter

_now = datetime.now(UTC)

MOCK_PLANS: list[dict[str, Any]] = [
    {
        "plan_id": "PLN-001",
        "title": "Handle Critical Transformer Incident — T102 Overheating",
        "goal": "Respond to critical transformer overheating incident at PeakVolt substation. Temperature 94°C exceeds emergency threshold of 85°C. Requires immediate dispatch, root cause analysis, and remediation.",
        "status": "completed",
        "confidence": 0.94,
        "agents_selected": [
            {"name": "Classification Agent", "status": "completed", "duration_ms": 320, "output": "Classified as Critical Transformer Incident — CUSTOMER_INTERACTION"},
            {"name": "Evidence Agent", "status": "completed", "duration_ms": 580, "output": "Collected EV-002 (Voltage Fluctuation), EV-003 (DGA Analysis: H2 85ppm, CH4 42ppm)"},
            {"name": "Knowledge Agent", "status": "completed", "duration_ms": 420, "output": "Retrieved DOC-003 (Oil Analysis Best Practices), DOC-007 (Siemens Transformer Manual)"},
            {"name": "Business Rule Agent", "status": "completed", "duration_ms": 310, "output": "Triggered RUL-002 (Voltage >5%), RUL-003 (DGA H2 >50ppm), RUL-004 (Maintenance Overdue)"},
            {"name": "Reasoning Agent", "status": "completed", "duration_ms": 890, "output": "Selected hypothesis: Winding insulation failure (confidence 0.87). Rejected: External grid disturbance (confidence 0.45)"},
            {"name": "Recommendation Agent", "status": "completed", "duration_ms": 450, "output": "Generated: R-001 (Schedule internal inspection, critical), R-003 (Oil reclamation, approved)"},
            {"name": "Explainability Agent", "status": "completed", "duration_ms": 380, "output": "Built narrative with evidence trace, rule triggers, confidence breakdown, and alternatives"},
        ],
        "total_duration_ms": 3350,
        "created_at": (_now - timedelta(hours=2)).isoformat(),
        "completed_at": (_now - timedelta(hours=1, minutes=55)).isoformat(),
        "recommendation_ids": ["R-001", "R-003"],
        "evidence_ids": ["EV-002", "EV-003"],
        "knowledge_ids": ["DOC-003", "DOC-007"],
        "rule_ids": ["RUL-002", "RUL-003", "RUL-004"],
    },
    {
        "plan_id": "PLN-002",
        "title": "Emergency Power Outage Response — Cable Fault Zone 3",
        "goal": "Respond to emergency power outage at PowerLine Dynamics. Underground cable fault caused 2h15m outage affecting 12 MW load. Coordinate repair, customer communication, and SLA management.",
        "status": "completed",
        "confidence": 0.91,
        "agents_selected": [
            {"name": "Classification Agent", "status": "completed", "duration_ms": 280, "output": "Classified as Emergency Outage — CUSTOMER_INTERACTION / EVIDENCE"},
            {"name": "Evidence Agent", "status": "completed", "duration_ms": 510, "output": "Collected EV-005 (Outage report, SCADA logs)"},
            {"name": "Knowledge Agent", "status": "completed", "duration_ms": 390, "output": "Retrieved DOC-004 (Emergency Response Playbook), DOC-005 (Grid Failure Playbook)"},
            {"name": "Business Rule Agent", "status": "completed", "duration_ms": 280, "output": "Triggered RUL-012 (SLA breach), RUL-013 (Emergency response)"},
            {"name": "Reasoning Agent", "status": "completed", "duration_ms": 760, "output": "Analyzed outage duration vs SLA commitments. Recommended compensation and process improvement"},
            {"name": "Recommendation Agent", "status": "completed", "duration_ms": 420, "output": "Generated: R-004 (Acoustic monitoring, critical), R-008 (SLA compensation, high)"},
            {"name": "Explainability Agent", "status": "completed", "duration_ms": 350, "output": "Built narrative with timeline, SLA breach analysis, and regulatory context"},
        ],
        "total_duration_ms": 2990,
        "created_at": (_now - timedelta(days=2)).isoformat(),
        "completed_at": (_now - timedelta(days=2, hours=-1, minutes=-45)).isoformat(),
        "recommendation_ids": ["R-004", "R-008"],
        "evidence_ids": ["EV-005", "EV-011"],
        "knowledge_ids": ["DOC-004", "DOC-005"],
        "rule_ids": ["RUL-012", "RUL-013"],
    },
    {
        "plan_id": "PLN-003",
        "title": "Wind Turbine WT-102 Predictive Maintenance",
        "goal": "Address wind turbine WT-102 bearing wear at 72% of failure threshold. Vibration increasing 12% MoM. Schedule inspection and order replacement parts proactively.",
        "status": "active",
        "confidence": 0.83,
        "agents_selected": [
            {"name": "Classification Agent", "status": "completed", "duration_ms": 260, "output": "Classified as Predictive Maintenance — CUSTOMER_INTERACTION"},
            {"name": "Evidence Agent", "status": "completed", "duration_ms": 480, "output": "Collected EV-012 (Vibration analysis, 12% MoM increase in 2-4kHz band)"},
            {"name": "Knowledge Agent", "status": "completed", "duration_ms": 370, "output": "Retrieved DOC-002 (Wind turbine inspection checklist), DOC-010 (Predictive maintenance whitepaper)"},
            {"name": "Business Rule Agent", "status": "completed", "duration_ms": 250, "output": "Triggered RUL-014 (Bearing wear threshold — advisory level)"},
            {"name": "Reasoning Agent", "status": "completed", "duration_ms": 690, "output": "Assessed wear acceleration rate. Recommended inspection within 14 days based on trend analysis"},
            {"name": "Recommendation Agent", "status": "completed", "duration_ms": 380, "output": "Generated: R-009 (Schedule bearing inspection, medium), Order replacement bearings"},
            {"name": "Explainability Agent", "status": "pending", "duration_ms": 0, "output": "Awaiting recommendation confirmation"},
        ],
        "total_duration_ms": 2430,
        "created_at": (_now - timedelta(days=4)).isoformat(),
        "completed_at": None,
        "recommendation_ids": ["R-009"],
        "evidence_ids": ["EV-012"],
        "knowledge_ids": ["DOC-002", "DOC-010"],
        "rule_ids": ["RUL-014"],
    },
    {
        "plan_id": "PLN-004",
        "title": "Battery Bank BB-101 Capacity Degradation Analysis",
        "goal": "Investigate 28% capacity loss in battery bank BB-101. Determine root cause (BMS firmware vs cell degradation) and recommend remediation plan.",
        "status": "completed",
        "confidence": 0.87,
        "agents_selected": [
            {"name": "Classification Agent", "status": "completed", "duration_ms": 300, "output": "Classified as Battery Degradation — EVIDENCE / ENERGY"},
            {"name": "Evidence Agent", "status": "completed", "duration_ms": 550, "output": "Collected EV-008 (Battery capacity test results), EV-014 (Historical performance data)"},
            {"name": "Knowledge Agent", "status": "completed", "duration_ms": 410, "output": "Retrieved DOC-006 (Battery maintenance guide), DOC-001 (Energy optimization playbook)"},
            {"name": "Business Rule Agent", "status": "completed", "duration_ms": 290, "output": "Triggered RUL-010 (Battery degradation threshold)"},
            {"name": "Reasoning Agent", "status": "completed", "duration_ms": 810, "output": "Determined BMS firmware issue primary cause (confidence 0.72), cell degradation secondary (confidence 0.45)"},
            {"name": "Recommendation Agent", "status": "completed", "duration_ms": 400, "output": "Generated: R-006 (Full capacity test, executed), BMS firmware update recommended"},
            {"name": "Explainability Agent", "status": "completed", "duration_ms": 360, "output": "Built narrative with capacity trend analysis, root cause differentiation, and cost-benefit"},
        ],
        "total_duration_ms": 3120,
        "created_at": (_now - timedelta(days=1)).isoformat(),
        "completed_at": (_now - timedelta(hours=12)).isoformat(),
        "recommendation_ids": ["R-006"],
        "evidence_ids": ["EV-008", "EV-014"],
        "knowledge_ids": ["DOC-006", "DOC-001"],
        "rule_ids": ["RUL-010"],
    },
]


class PlannerAdapter(BaseServiceAdapter):
    """Adapter for the Planner domain service — enterprise agent orchestration."""

    def get_domain(self) -> str:
        return "planner"

    def create_plan(self, params: dict[str, Any] | None = None) -> Any:
        return self._success_response(data={"plan_id": "plan-001", "status": "created", "params": params or {}})

    def get_plan(self, plan_id: str) -> Any:
        for plan in MOCK_PLANS:
            if plan["plan_id"] == plan_id:
                return self._success_response(data=plan)
        return self._success_response(data=None)

    def list_plans(self, status: str | None = None, limit: int = 20, offset: int = 0) -> Any:
        items = MOCK_PLANS
        if status:
            items = [p for p in items if p["status"] == status]
        items.sort(key=lambda p: p["created_at"], reverse=True)
        total = len(items)
        page = items[offset:offset + limit]
        return self._success_response(data={"plans": page, "total": total})

    def update_plan(self, plan_id: str, params: dict[str, Any] | None = None) -> Any:
        return self._success_response(data={"plan_id": plan_id, "status": "updated", "params": params or {}})

    def delete_plan(self, plan_id: str) -> Any:
        return self._success_response(data={"plan_id": plan_id, "status": "deleted"})
