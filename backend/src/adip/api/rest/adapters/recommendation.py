"""Recommendation service adapter."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from adip.api.rest.adapters.base import BaseServiceAdapter
from adip.api.rest.models.base import ApiResponse

_now = datetime.now(UTC)

MOCK_RECOMMENDATIONS: list[dict[str, Any]] = [
    {
        "id": "R-001", "title": "Schedule TF-102 Internal Inspection",
        "description": "Based on DGA analysis showing elevated hydrogen (85ppm) and methane (42ppm), schedule an internal inspection of TF-102 within 7 days to assess winding insulation condition.",
        "priority": "critical", "confidence": 0.87, "businessImpact": "Prevents catastrophic transformer failure affecting 25% of PeakVolt production capacity",
        "riskLevel": "high", "estimatedCost": 45000, "estimatedSavings": 320000, "timeline": "7 days", "source": "reasoning_engine",
        "status": "active", "reasoningId": "RSN-001",
        "evidenceIds": ["EV-002", "EV-003"], "ruleIds": ["RUL-002", "RUL-003", "RUL-004"], "knowledgeIds": ["DOC-003", "DOC-007"],
        "assetIds": ["TF-102"], "customerIds": ["C-1002"],
        "actions": [
            {"id": "A-001", "description": "Contact Siemens service team for TF-102 inspection", "assignedTo": "Maintenance Manager", "deadline": (datetime.now(UTC) + timedelta(days=7)).strftime("%Y-%m-%d"), "status": "in_progress"},
            {"id": "A-002", "description": "Order replacement gaskets and seals", "assignedTo": "Procurement", "deadline": (datetime.now(UTC) + timedelta(days=5)).strftime("%Y-%m-%d"), "status": "pending"},
        ],
        "createdAt": (_now - timedelta(hours=2)).isoformat(), "updatedAt": (_now - timedelta(hours=2)).isoformat(),
    },
    {
        "id": "R-002", "title": "Deploy Voltage Stabilization Equipment at Zone 4",
        "description": "Install dynamic voltage restorer (DVR) at PeakVolt Zone 4 to mitigate voltage fluctuations and protect production equipment from further damage.",
        "priority": "high", "confidence": 0.82, "businessImpact": "Eliminates production downtime caused by voltage fluctuations, saving ~$50K per incident",
        "riskLevel": "medium", "estimatedCost": 185000, "estimatedSavings": 600000, "timeline": "30 days", "source": "reasoning_engine",
        "status": "pending_approval", "reasoningId": "RSN-001",
        "evidenceIds": ["EV-002"], "ruleIds": ["RUL-002"], "knowledgeIds": ["DOC-003"],
        "assetIds": ["TF-101", "TF-102", "SN-105"], "customerIds": ["C-1002"],
        "actions": [
            {"id": "A-003", "description": "Submit engineering change request for DVR installation", "assignedTo": "Engineering Lead", "deadline": (datetime.now(UTC) + timedelta(days=14)).strftime("%Y-%m-%d"), "status": "pending"},
        ],
        "createdAt": (_now - timedelta(hours=1, minutes=30)).isoformat(), "updatedAt": (_now - timedelta(hours=1, minutes=30)).isoformat(),
    },
    {
        "id": "R-003", "title": "Oil Reclamation for Transformer TF-102",
        "description": "Perform oil reclamation/filtration on TF-102 to reduce moisture content and acidity levels. Improves dielectric strength and extends transformer life.",
        "priority": "high", "confidence": 0.85, "businessImpact": "Extends TF-102 life by 3-5 years. Avoids $500K replacement cost.",
        "riskLevel": "low", "estimatedCost": 28000, "estimatedSavings": 500000, "timeline": "14 days", "source": "reasoning_engine",
        "status": "approved", "reasoningId": "RSN-001",
        "evidenceIds": ["EV-003"], "ruleIds": ["RUL-004"], "knowledgeIds": ["DOC-003", "DOC-007"],
        "assetIds": ["TF-102"], "customerIds": ["C-1002"],
        "actions": [
            {"id": "A-004", "description": "Schedule oil reclamation with lab services", "assignedTo": "Maintenance Lead", "deadline": (datetime.now(UTC) + timedelta(days=7)).strftime("%Y-%m-%d"), "status": "completed", "completedAt": _now.isoformat()},
            {"id": "A-005", "description": "Post-reclamation DGA analysis", "assignedTo": "Lab Services", "deadline": (datetime.now(UTC) + timedelta(days=14)).strftime("%Y-%m-%d"), "status": "pending"},
        ],
        "createdAt": (_now - timedelta(hours=1)).isoformat(), "updatedAt": _now.isoformat(),
    },
    {
        "id": "R-004", "title": "Deploy Transformer TF-201 Acoustic Monitoring",
        "description": "Install permanent acoustic monitoring system on TF-201 following unusual noise detection. Enables early warning of winding loosening.",
        "priority": "critical", "confidence": 0.78, "businessImpact": "Prevents catastrophic failure of TF-201. Early warning allows planned maintenance vs emergency replacement.",
        "riskLevel": "medium", "estimatedCost": 35000, "estimatedSavings": 450000, "timeline": "14 days", "source": "reasoning_engine",
        "status": "active", "reasoningId": "RSN-002",
        "evidenceIds": ["EV-005"], "ruleIds": ["RUL-006"], "knowledgeIds": ["DOC-007"],
        "assetIds": ["TF-201"], "customerIds": ["C-1004"],
        "actions": [
            {"id": "A-006", "description": "Procure acoustic monitoring system", "assignedTo": "Procurement", "deadline": (datetime.now(UTC) + timedelta(days=10)).strftime("%Y-%m-%d"), "status": "in_progress"},
            {"id": "A-007", "description": "Schedule installation with electrical team", "assignedTo": "Engineering Lead", "deadline": (datetime.now(UTC) + timedelta(days=14)).strftime("%Y-%m-%d"), "status": "pending"},
        ],
        "createdAt": (_now - timedelta(hours=18)).isoformat(), "updatedAt": (_now - timedelta(hours=18)).isoformat(),
    },
    {
        "id": "R-005", "title": "Install Backup Generator Fuel Monitoring System",
        "description": "Implement automated fuel level monitoring for backup generators at Solaris facility. Addresses gap identified in grid failure readiness assessment.",
        "priority": "medium", "confidence": 0.92, "businessImpact": "Ensures backup power availability during grid failures. Regulatory compliance requirement.",
        "riskLevel": "low", "estimatedCost": 12000, "estimatedSavings": 0, "timeline": "21 days", "source": "reasoning_engine",
        "status": "active", "reasoningId": "RSN-002",
        "evidenceIds": ["EV-007"], "ruleIds": ["RUL-009"], "knowledgeIds": ["DOC-005"],
        "assetIds": ["BB-101"], "customerIds": ["C-1005"],
        "actions": [
            {"id": "A-008", "description": "Specify fuel monitoring system requirements", "assignedTo": "Engineering Lead", "deadline": (datetime.now(UTC) + timedelta(days=12)).strftime("%Y-%m-%d"), "status": "pending"},
        ],
        "createdAt": (_now - timedelta(days=2)).isoformat(), "updatedAt": (_now - timedelta(days=2)).isoformat(),
    },
    {
        "id": "R-006", "title": "Perform Full Capacity Test on BB-101",
        "description": "Execute full charge/discharge capacity test on battery storage BB-101 to quantify 18% capacity loss and determine if BMS firmware update or cell replacement is needed.",
        "priority": "high", "confidence": 0.82, "businessImpact": "Restores BB-101 to rated capacity. Extends useful life. Avoids $200K early replacement cost.",
        "riskLevel": "medium", "estimatedCost": 15000, "estimatedSavings": 200000, "timeline": "7 days", "source": "reasoning_engine",
        "status": "executed", "reasoningId": "RSN-004",
        "evidenceIds": ["EV-008", "EV-014"], "ruleIds": ["RUL-010"], "knowledgeIds": ["DOC-006"],
        "assetIds": ["BB-101"], "customerIds": ["C-1005"],
        "actions": [
            {"id": "A-009", "description": "Schedule capacity test with battery team", "assignedTo": "Maintenance Lead", "deadline": (datetime.now(UTC) + timedelta(days=3)).strftime("%Y-%m-%d"), "status": "completed", "completedAt": (_now - timedelta(hours=12)).isoformat()},
        ],
        "createdAt": (_now - timedelta(days=1)).isoformat(), "updatedAt": (_now - timedelta(hours=12)).isoformat(),
    },
    {
        "id": "R-007", "title": "Prepare Enterprise SLA Proposal for GridCore",
        "description": "Develop enterprise SLA tier proposal for GridCore Solutions. Revenue opportunity: $120K/yr. Include premium response times and dedicated support.",
        "priority": "low", "confidence": 0.79, "businessImpact": "New revenue stream: $120K annual. Strengthens customer relationship.",
        "riskLevel": "low", "estimatedCost": 5000, "estimatedSavings": 120000, "timeline": "45 days", "source": "customer_feedback",
        "status": "draft",
        "evidenceIds": ["EV-010"], "ruleIds": [], "knowledgeIds": ["DOC-009"],
        "assetIds": [], "customerIds": ["C-1006"],
        "actions": [],
        "createdAt": (_now - timedelta(days=3)).isoformat(), "updatedAt": (_now - timedelta(days=3)).isoformat(),
    },
    {
        "id": "R-008", "title": "Process EcoWatt SLA Breach Compensation",
        "description": "Process compensation claim for EcoWatt following 45-minute emergency response (exceeded 15-min SLA). Calculate service credit per SLA terms.",
        "priority": "high", "confidence": 0.91, "businessImpact": "Retains customer relationship. SLA compliance improvement needed.",
        "riskLevel": "medium", "estimatedCost": 25000, "estimatedSavings": 150000, "timeline": "14 days", "source": "compliance",
        "status": "pending_approval",
        "evidenceIds": ["EV-011"], "ruleIds": ["RUL-012", "RUL-013"], "knowledgeIds": ["DOC-009"],
        "assetIds": ["TF-202"], "customerIds": ["C-1008"],
        "actions": [
            {"id": "A-010", "description": "Calculate service credit amount", "assignedTo": "Customer Success", "deadline": (datetime.now(UTC) + timedelta(days=7)).strftime("%Y-%m-%d"), "status": "pending"},
            {"id": "A-011", "description": "Implement dispatch process improvements", "assignedTo": "Operations Manager", "deadline": (datetime.now(UTC) + timedelta(days=14)).strftime("%Y-%m-%d"), "status": "pending"},
        ],
        "createdAt": (_now - timedelta(days=3)).isoformat(), "updatedAt": (_now - timedelta(days=3)).isoformat(),
    },
    {
        "id": "R-009", "title": "Schedule WT-102 Bearing Inspection",
        "description": "Schedule bearing inspection for wind turbine WT-102 within 14 days. Bearing wear at 72% of failure threshold. Order replacement bearings proactively.",
        "priority": "medium", "confidence": 0.83, "businessImpact": "Prevents unplanned WT-102 downtime. Scheduled replacement costs 60% less than emergency repair.",
        "riskLevel": "medium", "estimatedCost": 18500, "estimatedSavings": 95000, "timeline": "14 days", "source": "reasoning_engine",
        "status": "active", "reasoningId": "RSN-003",
        "evidenceIds": ["EV-012"], "ruleIds": ["RUL-014"], "knowledgeIds": ["DOC-002", "DOC-010"],
        "assetIds": ["WT-102"], "customerIds": ["C-1009"],
        "actions": [
            {"id": "A-012", "description": "Schedule bearing inspection", "assignedTo": "Maintenance Lead", "deadline": (datetime.now(UTC) + timedelta(days=10)).strftime("%Y-%m-%d"), "status": "pending"},
            {"id": "A-013", "description": "Order replacement bearings", "assignedTo": "Procurement", "deadline": (datetime.now(UTC) + timedelta(days=7)).strftime("%Y-%m-%d"), "status": "in_progress"},
        ],
        "createdAt": (_now - timedelta(days=4)).isoformat(), "updatedAt": (_now - timedelta(days=4)).isoformat(),
    },
    {
        "id": "R-010", "title": "Install Additional Temperature Sensors at BlueCurrent",
        "description": "Install temperature sensors in Server Room B and Cooling Tower 3 as requested. Enables better thermal monitoring and predictive maintenance.",
        "priority": "low", "confidence": 0.72, "businessImpact": "Improved monitoring reduces risk of overheating incidents.",
        "riskLevel": "low", "estimatedCost": 8500, "estimatedSavings": 30000, "timeline": "30 days", "source": "customer_feedback",
        "status": "draft",
        "evidenceIds": [], "ruleIds": [], "knowledgeIds": [],
        "assetIds": ["SN-201", "SN-202"], "customerIds": ["C-1010"],
        "actions": [
            {"id": "A-014", "description": "Create sensor installation work order", "assignedTo": "Engineering Lead", "deadline": (datetime.now(UTC) + timedelta(days=21)).strftime("%Y-%m-%d"), "status": "pending"},
        ],
        "createdAt": (_now - timedelta(days=5)).isoformat(), "updatedAt": (_now - timedelta(days=5)).isoformat(),
    },
    {
        "id": "R-011", "title": "Implement NovaGrid SLA Improvement Plan",
        "description": "Develop and implement plan to improve NovaGrid SLA performance from 99.3% to 99.9% target. Focus areas: response time reduction and proactive monitoring.",
        "priority": "medium", "confidence": 0.94, "businessImpact": "Retains NovaGrid Premium SLA ($200K/yr). Avoids service credit penalties.",
        "riskLevel": "low", "estimatedCost": 35000, "estimatedSavings": 200000, "timeline": "60 days", "source": "reasoning_engine",
        "status": "approved", "reasoningId": "RSN-007",
        "evidenceIds": ["EV-013", "EV-014"], "ruleIds": ["RUL-007"], "knowledgeIds": ["DOC-001", "DOC-008"],
        "assetIds": ["SP-101", "SP-102", "SP-103"], "customerIds": ["C-1001"],
        "actions": [
            {"id": "A-015", "description": "Create SLA improvement roadmap", "assignedTo": "Operations Manager", "deadline": (datetime.now(UTC) + timedelta(days=14)).strftime("%Y-%m-%d"), "status": "in_progress"},
            {"id": "A-016", "description": "Implement proactive monitoring alerts", "assignedTo": "Engineering Lead", "deadline": (datetime.now(UTC) + timedelta(days=30)).strftime("%Y-%m-%d"), "status": "pending"},
        ],
        "createdAt": (_now - timedelta(days=6)).isoformat(), "updatedAt": (_now - timedelta(days=6)).isoformat(),
    },
]


class RecommendationAdapter(BaseServiceAdapter):
    def get_domain(self) -> str:
        return "recommendation"

    def recommend(self, query: str, params: dict[str, Any] | None = None) -> Any:
        return self._success_response(data={"recommendation_id": "rec-001", "query": query, "recommendations": [], "params": params or {}})

    def get_recommendation(self, recommendation_id: str) -> Any:
        for item in MOCK_RECOMMENDATIONS:
            if item["id"] == recommendation_id:
                return self._success_response(data=item)
        return self._success_response(data=None)

    def list_recommendations(
        self,
        status: str | None = None,
        priority: str | None = None,
        source: str | None = None,
        q: str = "",
        page: int | None = None,
        limit: int = 12,
    ) -> ApiResponse:
        items = MOCK_RECOMMENDATIONS
        if status:
            items = [r for r in items if r["status"] == status]
        if priority:
            items = [r for r in items if r["priority"] == priority]
        if source:
            items = [r for r in items if r["source"] == source]
        if q:
            query = q.lower()
            items = [r for r in items if query in r["title"].lower() or query in r["description"].lower()]
        items.sort(key=lambda r: r["createdAt"], reverse=True)
        total = len(items)
        page = page or 1
        start = (page - 1) * limit
        return self._success_response(data={"recommendations": items[start:start + limit], "total": total})
