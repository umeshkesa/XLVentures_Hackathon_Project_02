"""Action Manager service adapter — execution workflows tied to recommendations."""

from __future__ import annotations

from typing import Any

from adip.api.rest.adapters.base import BaseServiceAdapter

MOCK_ACTIONS: list[dict[str, Any]] = [
    {
        "action_id": "ACT-001",
        "recommendation_id": "R-001",
        "review_id": "REV-004",
        "title": "Preventive Maintenance — Solar Inverter Bank A",
        "status": "in_progress",
        "priority": "critical",
        "assigned_to": "j.smith@xlventure.com",
        "description": "Execute preventive maintenance on solar inverter bank A per schedule.",
        "created_at": "2026-06-26T08:00:00Z",
        "scheduled_date": "2026-07-01",
        "completed_at": None,
        "steps": [
            {"step": 1, "label": "Work order created", "status": "completed", "completed_at": "2026-06-26T09:00:00Z"},
            {"step": 2, "label": "Team assigned", "status": "completed", "completed_at": "2026-06-26T10:00:00Z"},
            {"step": 3, "label": "Parts requisition", "status": "completed", "completed_at": "2026-06-27T08:00:00Z"},
            {"step": 4, "label": "Site preparation", "status": "completed", "completed_at": "2026-06-28T07:00:00Z"},
            {"step": 5, "label": "Maintenance execution", "status": "in_progress", "completed_at": None},
            {"step": 6, "label": "Quality verification", "status": "pending", "completed_at": None},
            {"step": 7, "label": "Report and close", "status": "pending", "completed_at": None},
        ],
        "audit_history": [
            {"action": "created", "by": "System", "timestamp": "2026-06-26T08:00:00Z", "detail": "Action created from approved review REV-004"},
            {"action": "status_change", "by": "System", "timestamp": "2026-06-26T09:00:00Z", "detail": "Status changed to in_progress"},
        ],
    },
    {
        "action_id": "ACT-002",
        "recommendation_id": "R-009",
        "review_id": "REV-006",
        "title": "Customer Complaint Resolution — Bearing Wear",
        "status": "in_progress",
        "priority": "critical",
        "assigned_to": "a.williams@xlventure.com",
        "description": "Resolve customer complaint WND-003 bearing wear issue — replacement required.",
        "created_at": "2026-06-29T07:00:00Z",
        "scheduled_date": "2026-06-30",
        "completed_at": None,
        "steps": [
            {"step": 1, "label": "Diagnostic confirmation", "status": "completed", "completed_at": "2026-06-29T08:00:00Z"},
            {"step": 2, "label": "Bearing replacement parts ordered", "status": "completed", "completed_at": "2026-06-29T09:00:00Z"},
            {"step": 3, "label": "Technician dispatched", "status": "in_progress", "completed_at": None},
            {"step": 4, "label": "Replacement executed", "status": "pending", "completed_at": None},
            {"step": 5, "label": "Customer sign-off", "status": "pending", "completed_at": None},
        ],
        "audit_history": [
            {"action": "created", "by": "System", "timestamp": "2026-06-29T07:00:00Z", "detail": "Action created from approved review REV-006"},
            {"action": "status_change", "by": "System", "timestamp": "2026-06-29T08:00:00Z", "detail": "Diagnostic confirmed"},
        ],
    },
    {
        "action_id": "ACT-003",
        "recommendation_id": "R-005",
        "review_id": "REV-004",
        "title": "Customer SLA Compliance — Acme Industries",
        "status": "completed",
        "priority": "medium",
        "assigned_to": "m.johnson@xlventure.com",
        "description": "Implement SLA compliance updates for Acme Industries account.",
        "created_at": "2026-06-25T16:00:00Z",
        "scheduled_date": "2026-06-28",
        "completed_at": "2026-06-28T14:00:00Z",
        "steps": [
            {"step": 1, "label": "SLA terms reviewed", "status": "completed", "completed_at": "2026-06-25T17:00:00Z"},
            {"step": 2, "label": "Updates applied to CRM", "status": "completed", "completed_at": "2026-06-26T10:00:00Z"},
            {"step": 3, "label": "Customer notified", "status": "completed", "completed_at": "2026-06-26T11:00:00Z"},
            {"step": 4, "label": "Compliance verified", "status": "completed", "completed_at": "2026-06-28T14:00:00Z"},
        ],
        "audit_history": [
            {"action": "created", "by": "System", "timestamp": "2026-06-25T16:00:00Z", "detail": "Action created from approved review REV-004"},
            {"action": "completed", "by": "System", "timestamp": "2026-06-28T14:00:00Z", "detail": "All steps completed"},
        ],
    },
    {
        "action_id": "ACT-004",
        "recommendation_id": "R-004",
        "review_id": None,
        "title": "Wind Turbine Inspection — WND-007",
        "status": "pending",
        "priority": "high",
        "assigned_to": "",
        "description": "Schedule and perform wind turbine gearbox inspection for WND-007.",
        "created_at": "2026-06-29T10:00:00Z",
        "scheduled_date": "",
        "completed_at": None,
        "steps": [
            {"step": 1, "label": "Review pending — assign engineer", "status": "pending", "completed_at": None},
            {"step": 2, "label": "Schedule inspection", "status": "pending", "completed_at": None},
            {"step": 3, "label": "Perform inspection", "status": "pending", "completed_at": None},
            {"step": 4, "label": "Report findings", "status": "pending", "completed_at": None},
        ],
        "audit_history": [
            {"action": "created", "by": "AI Engine", "timestamp": "2026-06-29T10:00:00Z", "detail": "Action auto-generated from recommendation R-004"},
        ],
    },
    {
        "action_id": "ACT-005",
        "recommendation_id": "R-011",
        "review_id": None,
        "title": "Transformer Load Balancing",
        "status": "pending",
        "priority": "medium",
        "assigned_to": "",
        "description": "Re-balance transformer loads across substation A to prevent overloading.",
        "created_at": "2026-06-29T11:00:00Z",
        "scheduled_date": "",
        "completed_at": None,
        "steps": [
            {"step": 1, "label": "Review and assign", "status": "pending", "completed_at": None},
            {"step": 2, "label": "Load analysis", "status": "pending", "completed_at": None},
            {"step": 3, "label": "Implement rebalancing", "status": "pending", "completed_at": None},
            {"step": 4, "label": "Verify load distribution", "status": "pending", "completed_at": None},
        ],
        "audit_history": [
            {"action": "created", "by": "AI Engine", "timestamp": "2026-06-29T11:00:00Z", "detail": "Action auto-generated from recommendation R-011"},
        ],
    },
]


class ActionManagerAdapter(BaseServiceAdapter):
    def get_domain(self) -> str:
        return "action_manager"

    def create_action(self, action_type: str, params: dict[str, Any] | None = None) -> Any:
        action_id = f"ACT-{len(MOCK_ACTIONS) + 1:03d}"
        entry = {
            "action_id": action_id,
            "recommendation_id": (params or {}).get("recommendation_id", ""),
            "title": action_type,
            "status": "planned",
            "priority": (params or {}).get("priority", "medium"),
            "assigned_to": "",
            "description": (params or {}).get("description", ""),
            "created_at": "2026-06-29T12:00:00Z",
            "scheduled_date": "",
            "completed_at": None,
            "steps": [],
            "audit_history": [
                {"action": "created", "by": "System", "timestamp": "2026-06-29T12:00:00Z", "detail": f"Action created for recommendation {(params or {}).get('recommendation_id', '')}"},
            ],
        }
        MOCK_ACTIONS.append(entry)
        return self._success_response(data=entry)

    def get_action(self, action_id: str) -> Any:
        for a in MOCK_ACTIONS:
            if a["action_id"] == action_id:
                return self._success_response(data=a)
        return self._error_response(code="not_found", message=f"Action {action_id} not found")

    def list_actions(
        self,
        status: str | None = None,
        priority: str | None = None,
        q: str | None = None,
        page: int = 1,
        limit: int = 12,
    ) -> Any:
        filtered = list(MOCK_ACTIONS)
        if status:
            filtered = [a for a in filtered if a["status"] == status]
        if priority:
            filtered = [a for a in filtered if a["priority"] == priority]
        if q:
            ql = q.lower()
            filtered = [a for a in filtered if ql in a["title"].lower() or ql in a["action_id"].lower()]
        filtered.sort(key=lambda a: a.get("created_at", ""), reverse=True)
        total = len(filtered)
        start = (page - 1) * limit
        sliced = filtered[start : start + limit]
        return self._success_response(data={"actions": sliced, "total": total})

    def cancel_action(self, action_id: str) -> Any:
        for a in MOCK_ACTIONS:
            if a["action_id"] == action_id:
                a["status"] = "cancelled"
                a["audit_history"].append({"action": "cancelled", "by": "reviewer", "timestamp": "2026-06-29T12:00:00Z", "detail": "Action cancelled"})
                return self._success_response(data=a)
        return self._error_response(code="not_found", message=f"Action {action_id} not found")

    def update_status(self, action_id: str, status: str) -> Any:
        for a in MOCK_ACTIONS:
            if a["action_id"] == action_id:
                a["status"] = status
                a["audit_history"].append({"action": "status_change", "by": "System", "timestamp": "2026-06-29T12:00:00Z", "detail": f"Status changed to {status}"})
                return self._success_response(data=a)
        return self._error_response(code="not_found", message=f"Action {action_id} not found")
