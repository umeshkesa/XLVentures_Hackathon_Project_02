"""Explainability service adapter."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from adip.api.rest.adapters.base import BaseServiceAdapter
from adip.api.rest.models.base import ApiResponse

_now = datetime.now(UTC)

MOCK_EXPLANATIONS: list[dict[str, Any]] = [
    {
        "id": "EXP-001", "recommendationId": "R-001", "recommendationTitle": "Schedule TF-102 Internal Inspection",
        "narrative": "This recommendation was generated because DGA analysis of TF-102 transformer oil revealed elevated hydrogen (85ppm) and methane (42ppm), indicating partial discharge activity. Three business rules were triggered: voltage deviation >5%, DGA H2 >50ppm, and transformer maintenance overdue. The cross-referencing of knowledge documents (Oil Analysis Best Practices and Siemens Transformer Manual) confirmed the severity of the findings. The reasoning engine selected hypothesis of winding insulation failure (confidence 0.87) over external grid disturbance (confidence 0.45) based on evidence weight and rule triggers.",
        "confidence": 0.87, "createdAt": (_now - timedelta(hours=2)).isoformat(),
        "stages": [
            {"name": "Evidence Collection", "description": "Evidence gathered from SCADA, DGA, and customer reports", "details": ["EV-002: Voltage fluctuation report from PeakVolt Zone 4", "EV-003: TF-102 oil sample DGA analysis (H2: 85ppm, CH4: 42ppm)", "EV-009: Inverter error E-47 on SP-106"], "evidence": [{"id": "EV-002", "title": "Voltage Fluctuation Report", "confidence": 0.85}, {"id": "EV-003", "title": "TF-102 Oil Analysis", "confidence": 0.88}], "rules": [], "knowledge": [], "expanded": False},
            {"name": "Knowledge Retrieval", "description": "Cross-referenced evidence against knowledge base", "details": ["DOC-003: Oil Analysis Best Practices — confirms H2 >50ppm requires immediate investigation", "DOC-007: Siemens Transformer Maintenance Manual — section 4.2 covers partial discharge diagnosis"], "evidence": [], "rules": [], "knowledge": [{"id": "DOC-003", "title": "Oil Analysis Best Practices"}, {"id": "DOC-007", "title": "Siemens Transformer Manual"}], "expanded": False},
            {"name": "Rule Evaluation", "description": "Business rules evaluated against evidence", "details": ["RUL-002: Voltage deviation >5% — TRIGGERED (deviation 14.2%)", "RUL-003: DGA H2 >50ppm — TRIGGERED (H2 at 85ppm)", "RUL-004: Transformer maintenance due every 6 months — TRIGGERED (overdue)"], "evidence": [], "rules": [{"id": "RUL-002", "description": "Voltage deviation threshold", "triggered": True}, {"id": "RUL-003", "description": "DGA alert rules", "triggered": True}, {"id": "RUL-004", "description": "Transformer maintenance rules", "triggered": True}], "knowledge": [], "expanded": False},
            {"name": "Hypothesis Testing", "description": "Two hypotheses evaluated with confidence scoring", "details": ["Hypothesis 1 (confidence 0.87): TF-102 winding insulation failure — supported by DGA, voltage data, and rule triggers", "Hypothesis 2 (confidence 0.45): External grid disturbance — lower confidence due to insufficient evidence of grid-side anomalies"], "evidence": [], "rules": [], "knowledge": [], "expanded": False},
            {"name": "Recommendation Generation", "description": "Two recommendations generated from conclusion", "details": ["R-001 (Critical): Schedule internal inspection within 7 days", "R-003 (Approved): Perform oil reclamation within 14 days"], "evidence": [], "rules": [], "knowledge": [], "expanded": False},
        ],
        "confidenceBreakdown": [{"label": "Evidence Quality", "value": 0.88}, {"label": "Knowledge Relevance", "value": 0.85}, {"label": "Rule Consistency", "value": 0.91}, {"label": "Historical Accuracy", "value": 0.78}],
        "alternatives": [
            {"title": "External grid disturbance investigation", "confidence": 0.45, "reason": "Rejected due to insufficient evidence of grid-side anomalies and lack of rule triggers"},
            {"title": "Defer action and monitor for 30 days", "confidence": 0.18, "reason": "Rejected due to critical rule triggers (RUL-002, RUL-003) requiring immediate action"},
        ],
    },
    {
        "id": "EXP-002", "recommendationId": "R-009", "recommendationTitle": "Schedule WT-102 Bearing Inspection",
        "narrative": "Predictive maintenance analysis of wind turbine WT-102 identified bearing wear at 72% of failure threshold. Vibration data showed a 12% month-over-month increase in the 2-4 kHz band, consistent with bearing degradation patterns. Knowledge cross-reference with historical failure cases confirmed the pattern. The RUL-014 bearing wear threshold rule was evaluated at advisory level (not yet critical). Recommendation generated to schedule inspection within 14 days and proactively order replacement bearings.",
        "confidence": 0.83, "createdAt": (_now - timedelta(days=4)).isoformat(),
        "stages": [
            {"name": "Evidence Collection", "description": "Sensor data from wind turbine monitoring system", "details": ["EV-012: WT-102 vibration analysis showing 12% MoM increase", "EV-013: Monthly performance data showing efficiency decline"], "evidence": [{"id": "EV-012", "title": "WT-102 Vibration Analysis", "confidence": 0.83}], "rules": [], "knowledge": [], "expanded": False},
            {"name": "Knowledge Retrieval", "description": "Cross-referenced against maintenance knowledge", "details": ["DOC-002: Wind turbine inspection checklist — bearing inspection protocol found", "DOC-010: Predictive maintenance white paper — confirms bearing wear pattern"], "evidence": [], "rules": [], "knowledge": [{"id": "DOC-002", "title": "Wind Turbine Inspection Checklist"}, {"id": "DOC-010", "title": "Predictive Maintenance White Paper"}], "expanded": False},
            {"name": "Rule Evaluation", "description": "Bearing wear threshold evaluated", "details": ["RUL-014: Bearing wear threshold — triggered at advisory level (<80%)", "72% threshold: No immediate action required but monitoring recommended"], "evidence": [], "rules": [{"id": "RUL-014", "description": "Bearing wear threshold rule", "triggered": True}], "knowledge": [], "expanded": False},
            {"name": "Recommendation Generation", "description": "Preventive maintenance schedule generated", "details": ["R-009 (Medium): Schedule bearing inspection within 14 days", "Order replacement bearings proactively to minimize downtime"], "evidence": [], "rules": [], "knowledge": [], "expanded": False},
        ],
        "confidenceBreakdown": [{"label": "Evidence Quality", "value": 0.80}, {"label": "Knowledge Relevance", "value": 0.85}, {"label": "Rule Consistency", "value": 0.88}, {"label": "Historical Accuracy", "value": 0.79}],
        "alternatives": [
            {"title": "Immediate replacement without inspection", "confidence": 0.45, "reason": "Rejected — wear level at 72% does not warrant immediate replacement (overly conservative)"},
            {"title": "Continue monitoring for 60 days", "confidence": 0.30, "reason": "Rejected — 12% MoM increase suggests accelerating wear pattern requiring earlier intervention"},
        ],
    },
    {
        "id": "EXP-003", "recommendationId": "R-005", "recommendationTitle": "Install Backup Generator Fuel Monitoring System",
        "narrative": "Grid failure response readiness assessment identified a gap in backup generator fuel supply documentation at Solaris facility. The tabletop exercise (effectiveness 85%) revealed that manual fuel level checks are insufficient for regulatory compliance. Knowledge document DOC-005 (Grid Failure Playbook) was cross-referenced to identify the gap. Rule RUL-009 (Emergency response rules) requires automated fuel monitoring. Recommendation generated to implement automated fuel level monitoring for all backup generators.",
        "confidence": 0.92, "createdAt": (_now - timedelta(days=2)).isoformat(),
        "stages": [
            {"name": "Evidence Collection", "description": "Emergency drill and audit results", "details": ["EV-007: Grid emergency drill results (85% effectiveness)", "EV-004: ISO 50001 audit (94% compliance, minor gap noted)"], "evidence": [{"id": "EV-007", "title": "Grid Emergency Drill Results", "confidence": 0.94}], "rules": [], "knowledge": [], "expanded": False},
            {"name": "Knowledge Retrieval", "description": "Playbook and compliance documents reviewed", "details": ["DOC-005: Grid Failure Playbook v5 — fuel monitoring section requires automation", "ISO 50001 framework requires documented fuel management process"], "evidence": [], "rules": [], "knowledge": [{"id": "DOC-005", "title": "Grid Failure Playbook v5"}], "expanded": False},
            {"name": "Rule Evaluation", "description": "Compliance and emergency rules evaluated", "details": ["RUL-009: Emergency response rules — fuel monitoring automation required", "RUL-005: ISO compliance rules — documented fuel management required"], "evidence": [], "rules": [{"id": "RUL-009", "description": "Emergency response rules", "triggered": True}], "knowledge": [], "expanded": False},
            {"name": "Recommendation Generation", "description": "Remediation recommendation generated", "details": ["R-005 (Medium): Install automated fuel monitoring system (21 days, $12K)", "Addresses both regulatory compliance and operational readiness gaps"], "evidence": [], "rules": [], "knowledge": [], "expanded": False},
        ],
        "confidenceBreakdown": [{"label": "Evidence Quality", "value": 0.94}, {"label": "Knowledge Relevance", "value": 0.90}, {"label": "Rule Consistency", "value": 0.95}, {"label": "Historical Accuracy", "value": 0.88}],
        "alternatives": [
            {"title": "Manual fuel log improvement only", "confidence": 0.35, "reason": "Rejected — does not meet regulatory automation requirement per RUL-009"},
        ],
    },
]


class ExplainabilityAdapter(BaseServiceAdapter):
    def get_domain(self) -> str:
        return "explainability"

    def explain(self, decision_id: str, params: dict[str, Any] | None = None) -> Any:
        return self._success_response(data={"explanation_id": "exp-001", "decision_id": decision_id, "narrative": "Deterministic explanation.", "params": params or {}})

    def get_explanation(self, explanation_id: str) -> Any:
        for item in MOCK_EXPLANATIONS:
            if item["id"] == explanation_id:
                return self._success_response(data=item)
        return self._success_response(data=None)

    def list_explanations(self, page: int | None = None, limit: int = 12) -> ApiResponse:
        items = MOCK_EXPLANATIONS
        items.sort(key=lambda e: e["createdAt"], reverse=True)
        total = len(items)
        page = page or 1
        start = (page - 1) * limit
        return self._success_response(data={"explanations": items[start:start + limit], "total": total})
