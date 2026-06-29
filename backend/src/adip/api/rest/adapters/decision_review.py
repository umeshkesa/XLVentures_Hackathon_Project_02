"""Decision Review service adapter — HITL reviews tied to recommendations."""

from __future__ import annotations

from typing import Any

from adip.api.rest.adapters.base import BaseServiceAdapter

MOCK_REVIEWS: list[dict[str, Any]] = [
    {
        "review_id": "REV-001",
        "recommendation_id": "R-001",
        "recommendation_title": "Preventive Maintenance — Solar Inverter Bank A",
        "status": "pending",
        "priority": "critical",
        "assigned_engineer": "",
        "comments": [],
        "audit_history": [
            {"action": "created", "by": "AI Engine", "timestamp": "2026-06-28T08:00:00Z", "detail": "Recommendation generated for energy asset SOL-001"},
        ],
        "created_at": "2026-06-28T08:00:00Z",
        "updated_at": "2026-06-28T08:00:00Z",
    },
    {
        "review_id": "REV-002",
        "recommendation_id": "R-002",
        "recommendation_title": "Wind Turbine Gearbox Oil Replacement",
        "status": "pending",
        "priority": "high",
        "assigned_engineer": "",
        "comments": [],
        "audit_history": [
            {"action": "created", "by": "AI Engine", "timestamp": "2026-06-27T14:30:00Z", "detail": "Recommendation generated for asset WND-003"},
        ],
        "created_at": "2026-06-27T14:30:00Z",
        "updated_at": "2026-06-27T14:30:00Z",
    },
    {
        "review_id": "REV-003",
        "recommendation_id": "R-003",
        "recommendation_title": "Battery Storage Capacity Upgrade — Substation B",
        "status": "under_review",
        "priority": "medium",
        "assigned_engineer": "j.smith@xlventure.com",
        "comments": [
            {"id": "C-001", "author": "j.smith@xlventure.com", "text": "Reviewed initial analysis. Need more data on load patterns.", "timestamp": "2026-06-28T09:15:00Z"},
        ],
        "audit_history": [
            {"action": "created", "by": "AI Engine", "timestamp": "2026-06-26T10:00:00Z", "detail": "Recommendation generated based on capacity forecast"},
            {"action": "assigned", "by": "System", "timestamp": "2026-06-26T11:00:00Z", "detail": "Assigned to j.smith@xlventure.com"},
            {"action": "comment_added", "by": "j.smith@xlventure.com", "timestamp": "2026-06-28T09:15:00Z", "detail": "Requested additional load pattern data"},
        ],
        "created_at": "2026-06-26T10:00:00Z",
        "updated_at": "2026-06-28T09:15:00Z",
    },
    {
        "review_id": "REV-004",
        "recommendation_id": "R-005",
        "recommendation_title": "Customer SLA Compliance — Acme Industries",
        "status": "approved",
        "priority": "medium",
        "assigned_engineer": "m.johnson@xlventure.com",
        "comments": [
            {"id": "C-002", "author": "m.johnson@xlventure.com", "text": "Approved — aligned with SLA terms.", "timestamp": "2026-06-25T16:00:00Z"},
        ],
        "audit_history": [
            {"action": "created", "by": "AI Engine", "timestamp": "2026-06-24T08:00:00Z", "detail": "SLA compliance analysis triggered"},
            {"action": "assigned", "by": "System", "timestamp": "2026-06-24T09:00:00Z", "detail": "Assigned to m.johnson@xlventure.com"},
            {"action": "approved", "by": "m.johnson@xlventure.com", "timestamp": "2026-06-25T16:00:00Z", "detail": "Recommendation approved for execution"},
        ],
        "created_at": "2026-06-24T08:00:00Z",
        "updated_at": "2026-06-25T16:00:00Z",
    },
    {
        "review_id": "REV-005",
        "recommendation_id": "R-008",
        "recommendation_title": "Transformer Oil Analysis — TX-002",
        "status": "rejected",
        "priority": "high",
        "assigned_engineer": "",
        "comments": [
            {"id": "C-003", "author": "l.chen@xlventure.com", "text": "Insufficient evidence — oil analysis data is stale. Request retest before proceeding.", "timestamp": "2026-06-23T11:30:00Z"},
        ],
        "audit_history": [
            {"action": "created", "by": "AI Engine", "timestamp": "2026-06-22T07:00:00Z", "detail": "Predictive maintenance alert for TX-002"},
            {"action": "rejected", "by": "l.chen@xlventure.com", "timestamp": "2026-06-23T11:30:00Z", "detail": "Rejected — stale oil analysis data; retest required"},
        ],
        "created_at": "2026-06-22T07:00:00Z",
        "updated_at": "2026-06-23T11:30:00Z",
    },
    {
        "review_id": "REV-006",
        "recommendation_id": "R-009",
        "recommendation_title": "Customer Complaint Resolution — Bearing Wear",
        "status": "approved",
        "priority": "critical",
        "assigned_engineer": "a.williams@xlventure.com",
        "comments": [
            {"id": "C-004", "author": "a.williams@xlventure.com", "text": "Critical issue — scheduling immediate replacement.", "timestamp": "2026-06-29T07:00:00Z"},
        ],
        "audit_history": [
            {"action": "created", "by": "AI Engine", "timestamp": "2026-06-28T18:00:00Z", "detail": "Complaint analysis — bearing wear pattern detected"},
            {"action": "assigned", "by": "System", "timestamp": "2026-06-28T19:00:00Z", "detail": "Assigned to a.williams@xlventure.com"},
            {"action": "approved", "by": "a.williams@xlventure.com", "timestamp": "2026-06-29T07:00:00Z", "detail": "Approved for immediate execution"},
        ],
        "created_at": "2026-06-28T18:00:00Z",
        "updated_at": "2026-06-29T07:00:00Z",
    },
    {
        "review_id": "REV-007",
        "recommendation_id": "R-010",
        "recommendation_title": "Compliance Update — OSHA 2026 Standards",
        "status": "pending",
        "priority": "medium",
        "assigned_engineer": "",
        "comments": [],
        "audit_history": [
            {"action": "created", "by": "Rule Engine", "timestamp": "2026-06-29T06:00:00Z", "detail": "Regulatory change detected — OSHA 2026"},
        ],
        "created_at": "2026-06-29T06:00:00Z",
        "updated_at": "2026-06-29T06:00:00Z",
    },
]


class DecisionReviewAdapter(BaseServiceAdapter):
    def get_domain(self) -> str:
        return "decision_review"

    def create_review(self, decision_id: str, params: dict[str, Any] | None = None) -> Any:
        review_id = f"REV-{len(MOCK_REVIEWS) + 1:03d}"
        entry = {
            "review_id": review_id,
            "recommendation_id": decision_id,
            "recommendation_title": f"Recommendation {decision_id}",
            "status": "pending",
            "priority": (params or {}).get("priority", "medium"),
            "assigned_engineer": "",
            "comments": [],
            "audit_history": [
                {"action": "created", "by": "AI Engine", "timestamp": "2026-06-29T12:00:00Z", "detail": f"Review created for recommendation {decision_id}"},
            ],
            "created_at": "2026-06-29T12:00:00Z",
            "updated_at": "2026-06-29T12:00:00Z",
        }
        MOCK_REVIEWS.append(entry)
        return self._success_response(data=entry)

    def get_review(self, review_id: str) -> Any:
        rid = review_id.upper()
        for r in MOCK_REVIEWS:
            if r["review_id"] == rid:
                return self._success_response(data=r)
        return self._error_response(code="not_found", message=f"Review {review_id} not found")

    def list_reviews(
        self,
        status: str | None = None,
        priority: str | None = None,
        q: str | None = None,
        page: int = 1,
        limit: int = 12,
    ) -> Any:
        filtered = list(MOCK_REVIEWS)
        if status:
            filtered = [r for r in filtered if r["status"] == status]
        if priority:
            filtered = [r for r in filtered if r["priority"] == priority]
        if q:
            ql = q.lower()
            filtered = [
                r
                for r in filtered
                if ql in r["recommendation_title"].lower() or ql in r["review_id"].lower()
            ]
        filtered.sort(key=lambda r: r["updated_at"], reverse=True)
        total = len(filtered)
        start = (page - 1) * limit
        sliced = filtered[start : start + limit]
        return self._success_response(data={"reviews": sliced, "total": total})

    def approve(self, review_id: str, comment: str = "") -> Any:
        rid = review_id.upper()
        for r in MOCK_REVIEWS:
            if r["review_id"] == rid:
                r["status"] = "approved"
                r["updated_at"] = "2026-06-29T12:00:00Z"
                entry = {"action": "approved", "by": "reviewer", "timestamp": "2026-06-29T12:00:00Z", "detail": comment or "Approved for execution"}
                r["audit_history"].append(entry)
                if comment:
                    r["comments"].append({"id": f"C-{len(r['comments'])+1:03d}", "author": "reviewer", "text": comment, "timestamp": "2026-06-29T12:00:00Z"})
                return self._success_response(data=r)
        return self._error_response(code="not_found", message=f"Review {review_id} not found")

    def reject(self, review_id: str, reason: str = "") -> Any:
        rid = review_id.upper()
        for r in MOCK_REVIEWS:
            if r["review_id"] == rid:
                r["status"] = "rejected"
                r["updated_at"] = "2026-06-29T12:00:00Z"
                entry = {"action": "rejected", "by": "reviewer", "timestamp": "2026-06-29T12:00:00Z", "detail": reason or "Rejected"}
                r["audit_history"].append(entry)
                if reason:
                    r["comments"].append({"id": f"C-{len(r['comments'])+1:03d}", "author": "reviewer", "text": reason, "timestamp": "2026-06-29T12:00:00Z"})
                return self._success_response(data=r)
        return self._error_response(code="not_found", message=f"Review {review_id} not found")

    def request_info(self, review_id: str, question: str = "") -> Any:
        rid = review_id.upper()
        for r in MOCK_REVIEWS:
            if r["review_id"] == rid:
                r["status"] = "more_info_needed"
                r["updated_at"] = "2026-06-29T12:00:00Z"
                entry = {"action": "more_info_requested", "by": "reviewer", "timestamp": "2026-06-29T12:00:00Z", "detail": question or "Additional information requested"}
                r["audit_history"].append(entry)
                if question:
                    r["comments"].append({"id": f"C-{len(r['comments'])+1:03d}", "author": "reviewer", "text": f"Request: {question}", "timestamp": "2026-06-29T12:00:00Z"})
                return self._success_response(data=r)
        return self._error_response(code="not_found", message=f"Review {review_id} not found")

    def add_comment(self, review_id: str, text: str, author: str = "reviewer") -> Any:
        rid = review_id.upper()
        for r in MOCK_REVIEWS:
            if r["review_id"] == rid:
                comment = {"id": f"C-{len(r['comments'])+1:03d}", "author": author, "text": text, "timestamp": "2026-06-29T12:00:00Z"}
                r["comments"].append(comment)
                r["updated_at"] = "2026-06-29T12:00:00Z"
                r["audit_history"].append({"action": "comment_added", "by": author, "timestamp": "2026-06-29T12:00:00Z", "detail": text})
                return self._success_response(data=r)
        return self._error_response(code="not_found", message=f"Review {review_id} not found")

    def assign_engineer(self, review_id: str, engineer: str) -> Any:
        rid = review_id.upper()
        for r in MOCK_REVIEWS:
            if r["review_id"] == rid:
                r["assigned_engineer"] = engineer
                r["updated_at"] = "2026-06-29T12:00:00Z"
                r["audit_history"].append({"action": "assigned", "by": "reviewer", "timestamp": "2026-06-29T12:00:00Z", "detail": f"Assigned to {engineer}"})
                return self._success_response(data=r)
        return self._error_response(code="not_found", message=f"Review {review_id} not found")

    def schedule_action(self, review_id: str, scheduled_date: str, notes: str = "") -> Any:
        rid = review_id.upper()
        for r in MOCK_REVIEWS:
            if r["review_id"] == rid:
                r["status"] = "scheduled"
                r["updated_at"] = scheduled_date
                r["audit_history"].append({"action": "scheduled", "by": "reviewer", "timestamp": scheduled_date, "detail": f"Scheduled for {scheduled_date}. {notes}"})
                return self._success_response(data=r)
        return self._error_response(code="not_found", message=f"Review {review_id} not found")
