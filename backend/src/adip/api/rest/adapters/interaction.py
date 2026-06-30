"""Interaction service adapter — energy domain customer interactions."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from adip.api.rest.adapters.base import BaseServiceAdapter
from adip.api.rest.models.base import ApiResponse

_now = datetime.now(UTC)

MOCK_INTERACTIONS: list[dict[str, Any]] = [
    {
        "id": "INT-001", "type": "complaint",
        "subject": "Transformer T102 Overheating — Temperature 94°C",
        "content": "Customer reports Transformer T102 at PeakVolt substation is overheating. Temperature reading 94°C against normal operating range of 40-85°C. Priority: Critical. Immediate dispatch required.",
        "date": (_now - timedelta(hours=2)).isoformat(),
        "agent": "Sarah Chen", "customerId": "C-1002", "customerName": "PeakVolt Systems",
        "relatedAssets": ["TF-102"], "relatedEvidence": ["EV-002", "EV-003"],
        "relatedRecommendations": ["R-001", "R-003"],
        "relatedPlannerRun": "PLN-001",
        "attachments": [{"name": "temperature_log_t102.csv", "url": "#", "size": 45000}],
        "status": "escalated",
    },
    {
        "id": "INT-002", "type": "complaint",
        "subject": "Voltage Fluctuation in Zone 4 — Production Downtime",
        "content": "Customer reports voltage fluctuations in Zone 4 production area over the past 48 hours. Fluctuations between 380V-420V causing production equipment to trip. Estimated downtime: 12 hours. Loss: $50K.",
        "date": (_now - timedelta(hours=5)).isoformat(),
        "agent": "Mike Rivera", "customerId": "C-1002", "customerName": "PeakVolt Systems",
        "relatedAssets": ["TF-101", "SN-105"], "relatedEvidence": ["EV-002"],
        "relatedRecommendations": ["R-002"],
        "relatedPlannerRun": "PLN-001",
        "attachments": [], "status": "escalated",
    },
    {
        "id": "INT-003", "type": "call_transcript",
        "subject": "Wind Turbine WT-102 Vibration Alert",
        "content": "Call transcript: Site operator reports unusual vibration in Wind Turbine WT-102. Vibration levels at 7.2 mm/s (threshold: 4.5 mm/s). Bearing temperature elevated at 72°C. Operator recommends inspection within 24 hours.",
        "date": (_now - timedelta(hours=8)).isoformat(),
        "agent": "John Smith", "customerId": "C-1009", "customerName": "TerraVolt Corp",
        "relatedAssets": ["WT-102"], "relatedEvidence": ["EV-012"],
        "relatedRecommendations": ["R-009"],
        "relatedPlannerRun": "PLN-003",
        "attachments": [{"name": "vibration_report_wt102.txt", "url": "#", "size": 28000}],
        "status": "resolved",
    },
    {
        "id": "INT-004", "type": "service_request",
        "subject": "Battery Bank BB-101 Degradation Assessment",
        "content": "Requesting technical assessment of Battery Bank BB-101. Capacity has dropped to 72% of rated capacity. Degradation rate accelerated over last 3 months. Need root cause analysis and remediation plan.",
        "date": (_now - timedelta(hours=12)).isoformat(),
        "agent": "David Kim", "customerId": "C-1005", "customerName": "Solaris Utilities",
        "relatedAssets": ["BB-101"], "relatedEvidence": ["EV-008", "EV-014"],
        "relatedRecommendations": ["R-006"],
        "relatedPlannerRun": "PLN-004",
        "attachments": [{"name": "battery_capacity_report.pdf", "url": "#", "size": 340000}],
        "status": "pending",
    },
    {
        "id": "INT-005", "type": "email",
        "subject": "Solar Inverter SP-106 Error E-47 — Remote Diagnostic Required",
        "content": "Solar inverter SP-106 has triggered error code E-47 (DC bus overvoltage). Remote diagnostics initiated. Preliminary analysis suggests capacitor bank failure. Requesting replacement part order.",
        "date": (_now - timedelta(days=1)).isoformat(),
        "agent": "Emily Park", "customerId": "C-1001", "customerName": "NovaGrid Energy",
        "relatedAssets": ["SP-106"], "relatedEvidence": ["EV-009"],
        "relatedRecommendations": [],
        "relatedPlannerRun": None,
        "attachments": [{"name": "inverter_error_log.csv", "url": "#", "size": 15600}],
        "status": "resolved",
    },
    {
        "id": "INT-006", "type": "complaint",
        "subject": "Unexpected Energy Spike — SCADA Alarm 47B",
        "content": "SCADA alarm 47B triggered: Unexpected energy spike detected at GridCore facility. Spike reached 14.2 MW against baseline of 8.5 MW. Duration: 3.4 seconds. Possible equipment fault or grid disturbance.",
        "date": (_now - timedelta(days=1)).isoformat(),
        "agent": "Mike Rivera", "customerId": "C-1006", "customerName": "GridCore Solutions",
        "relatedAssets": [], "relatedEvidence": ["EV-010"],
        "relatedRecommendations": [],
        "relatedPlannerRun": None,
        "attachments": [], "status": "escalated",
    },
    {
        "id": "INT-007", "type": "crm_update",
        "subject": "Emergency Outage Report — PowerLine Zone 3",
        "content": "CRM Update: Emergency outage reported at PowerLine Dynamics Zone 3. Duration: 2 hours 15 minutes. Affected loads: 12 MW. Root cause: Underground cable fault. Repairs underway, estimated restoration: 6 hours.",
        "date": (_now - timedelta(days=2)).isoformat(),
        "agent": "Sarah Chen", "customerId": "C-1004", "customerName": "PowerLine Dynamics",
        "relatedAssets": ["TF-201"], "relatedEvidence": ["EV-005"],
        "relatedRecommendations": ["R-004"],
        "relatedPlannerRun": "PLN-002",
        "attachments": [], "status": "resolved",
    },
    {
        "id": "INT-008", "type": "chat",
        "subject": "Predictive Maintenance Alert — Cooling Tower 3",
        "content": "Chat conversation: Predictive maintenance system alert for Cooling Tower 3 at BlueCurrent facility. Vibration sensor reading 35% above baseline. Automated recommendation: Schedule bearing inspection within 7 days.",
        "date": (_now - timedelta(days=3)).isoformat(),
        "agent": "Emily Park", "customerId": "C-1010", "customerName": "BlueCurrent Ltd",
        "relatedAssets": ["SN-201", "SN-202"], "relatedEvidence": [],
        "relatedRecommendations": ["R-010"],
        "relatedPlannerRun": None,
        "attachments": [], "status": "resolved",
    },
    {
        "id": "INT-009", "type": "complaint",
        "subject": "SCADA Communication Failure — Solar Farm A",
        "content": "SCADA communication failure at Solar Farm A. Lost telemetry from 23 of 47 inverters. Affected data: power output, temperature, grid synchronization status. Estimated data gap: 4 hours 30 minutes.",
        "date": (_now - timedelta(days=4)).isoformat(),
        "agent": "Mike Rivera", "customerId": "C-1003", "customerName": "GreenCircuit Inc",
        "relatedAssets": ["SP-103", "SP-104"], "relatedEvidence": ["EV-004"],
        "relatedRecommendations": [],
        "relatedPlannerRun": None,
        "attachments": [], "status": "pending",
    },
    {
        "id": "INT-010", "type": "feedback",
        "subject": "Transformer Predictive Maintenance Success",
        "content": "Customer feedback: The predictive maintenance alert on TF-102 helped us identify overheating before failure. The recommended oil reclamation was completed successfully. Highly satisfied with the proactive approach.",
        "date": (_now - timedelta(days=5)).isoformat(),
        "agent": "Lisa Wang", "customerId": "C-1002", "customerName": "PeakVolt Systems",
        "relatedAssets": ["TF-102"], "relatedEvidence": ["EV-003"],
        "relatedRecommendations": ["R-003"],
        "relatedPlannerRun": "PLN-001",
        "attachments": [], "status": "resolved",
    },
    {
        "id": "INT-011", "type": "service_request",
        "subject": "Emergency Cooling System Repair — Transformer TF-201",
        "content": "Emergency service request: Cooling system failure on Transformer TF-201 at PowerLine Dynamics. Oil temperature rising at 2°C/hour. Request immediate mobile cooling unit deployment.",
        "date": (_now - timedelta(days=6)).isoformat(),
        "agent": "David Kim", "customerId": "C-1004", "customerName": "PowerLine Dynamics",
        "relatedAssets": ["TF-201"], "relatedEvidence": ["EV-005"],
        "relatedRecommendations": ["R-004"],
        "relatedPlannerRun": "PLN-002",
        "attachments": [], "status": "pending",
    },
    {
        "id": "INT-012", "type": "email",
        "subject": "Monthly Performance Report — 4.2 GWh Output",
        "content": "Monthly performance report June 2026: Total energy output 4.2 GWh. Efficiency 94.3%. Availability 99.1%. Notable: Solar Farm B exceeded target by 12%. Wind Farm A below target due to low wind days.",
        "date": (_now - timedelta(days=7)).isoformat(),
        "agent": "Sarah Chen", "customerId": "C-1001", "customerName": "NovaGrid Energy",
        "relatedAssets": ["SP-101", "SP-102", "SP-103"],
        "relatedEvidence": ["EV-013", "EV-014"],
        "relatedRecommendations": ["R-011"],
        "relatedPlannerRun": None,
        "attachments": [{"name": "monthly_report_june_2026.pdf", "url": "#", "size": 1200000}],
        "status": "resolved",
    },
]


class InteractionAdapter(BaseServiceAdapter):
    def get_domain(self) -> str:
        return "interaction"

    def list(
        self,
        type: str | None = None,
        status: str | None = None,
        search: str | None = None,
        customer_id: str | None = None,
        page: int = 1,
        limit: int = 12,
    ) -> ApiResponse:
        items = MOCK_INTERACTIONS
        if type:
            items = [i for i in items if i["type"] == type]
        if status:
            items = [i for i in items if i["status"] == status]
        if customer_id:
            items = [i for i in items if i["customerId"] == customer_id]
        if search:
            q = search.lower()
            items = [i for i in items if q in i["subject"].lower() or q in i["content"].lower() or q in i["customerName"].lower()]
        items.sort(key=lambda i: i["date"], reverse=True)
        total = len(items)
        start = (page - 1) * limit
        return self._success_response(data={"items": items[start:start + limit], "total": total})

    def get_by_id(self, interaction_id: str) -> ApiResponse:
        for item in MOCK_INTERACTIONS:
            if item["id"] == interaction_id:
                return self._success_response(data=item)
        return self._success_response(data=None)

    def get_timeline(
        self,
        customer_id: str | None = None,
        type: str | None = None,
    ) -> ApiResponse:
        items = MOCK_INTERACTIONS
        if customer_id:
            items = [i for i in items if i["customerId"] == customer_id]
        if type:
            items = [i for i in items if i["type"] == type]
        items.sort(key=lambda i: i["date"], reverse=True)
        groups: dict[str, list[dict[str, Any]]] = {}
        for item in items:
            dt = datetime.fromisoformat(item["date"])
            day = dt.strftime("%A, %B %d, %Y")
            groups.setdefault(day, []).append(item)
        return self._success_response(
            data={"groups": [{"date": d, "interactions": g} for d, g in groups.items()]}
        )
