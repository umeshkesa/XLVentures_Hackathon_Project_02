"""ReviewerAssignmentEngine — deterministic reviewer assignment for reviews.

Manages a pool of available reviewers and assigns them to review
requests based on strategy, role match, and workload capacity.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.review.execution.models import ReviewerAssignment

log = structlog.get_logger(__name__)


class ReviewerAssignmentEngine:
    """In-memory reviewer pool with deterministic assignment logic."""

    def __init__(self) -> None:
        self._available_reviewers: dict[str, dict[str, Any]] = {}

    def register_reviewer(
        self,
        reviewer_id: str,
        name: str,
        role: str,
        expertise: float = 0.5,
        max_concurrent: int = 5,
    ) -> None:
        """Register a new reviewer into the available pool."""
        self._available_reviewers[reviewer_id] = {
            "name": name,
            "role": role,
            "expertise": expertise,
            "workload": 0,
            "max_concurrent": max_concurrent,
            "is_active": True,
        }
        log.info(
            "reviewer_assignment.register_reviewer",
            reviewer_id=reviewer_id,
            name=name,
            role=role,
        )

    def unregister_reviewer(self, reviewer_id: str) -> bool:
        """Remove a reviewer from the pool. Returns True if removed."""
        if reviewer_id not in self._available_reviewers:
            log.warning(
                "reviewer_assignment.unregister_reviewer.not_found",
                reviewer_id=reviewer_id,
            )
            return False
        del self._available_reviewers[reviewer_id]
        log.info(
            "reviewer_assignment.unregister_reviewer",
            reviewer_id=reviewer_id,
        )
        return True

    def assign_reviewers(
        self,
        request: Any,
        strategy: str,
        count: int = 1,
    ) -> list[ReviewerAssignment]:
        """Assign reviewers to a review request.

        Deterministic placeholder: filters available, active reviewers
        whose workload < max_concurrent, optionally matching role, then
        selects up to *count* candidates.
        """
        candidates = [
            (rid, info)
            for rid, info in self._available_reviewers.items()
            if info["is_active"] and info["workload"] < info["max_concurrent"]
        ]

        strategy_role = self._resolve_strategy_role(strategy)
        if strategy_role:
            candidates = [
                (rid, info) for rid, info in candidates if info["role"] == strategy_role
            ]

        selected = candidates[:count]
        assignments: list[ReviewerAssignment] = []
        for rid, info in selected:
            info["workload"] += 1
            assignments.append(
                ReviewerAssignment(
                    reviewer_id=rid,
                    reviewer_name=info["name"],
                    reviewer_role=info["role"],
                    expertise_score=info["expertise"],
                    current_workload=info["workload"],
                    is_available=True,
                )
            )

        log.info(
            "reviewer_assignment.assign_reviewers",
            strategy=strategy,
            requested=count,
            assigned=len(assignments),
        )
        return assignments

    def get_available_reviewers(self) -> list[dict[str, Any]]:
        """Return a list of all currently registered reviewer records."""
        result = [
            {**info, "reviewer_id": rid}
            for rid, info in self._available_reviewers.items()
        ]
        log.info(
            "reviewer_assignment.get_available_reviewers",
            count=len(result),
        )
        return result

    def get_reviewer_workload(self, reviewer_id: str) -> int:
        """Return the current workload count for a reviewer."""
        info = self._available_reviewers.get(reviewer_id)
        if info is None:
            log.warning(
                "reviewer_assignment.get_reviewer_workload.not_found",
                reviewer_id=reviewer_id,
            )
            return 0
        return info["workload"]

    def update_availability(self, reviewer_id: str, is_available: bool) -> bool:
        """Update the active status of a reviewer. Returns True on success."""
        info = self._available_reviewers.get(reviewer_id)
        if info is None:
            log.warning(
                "reviewer_assignment.update_availability.not_found",
                reviewer_id=reviewer_id,
            )
            return False
        info["is_active"] = is_available
        log.info(
            "reviewer_assignment.update_availability",
            reviewer_id=reviewer_id,
            is_available=is_available,
        )
        return True

    def _resolve_strategy_role(self, strategy: str) -> str | None:
        """Map an approval strategy to a preferred reviewer role."""
        mapping: dict[str, str] = {
            "SINGLE_REVIEW": "SUPERVISOR",
            "SEQUENTIAL": "MANAGER",
            "PARALLEL": "ENGINEER",
            "MULTI_LEVEL": "ADMINISTRATOR",
            "EMERGENCY": "ADMINISTRATOR",
        }
        return mapping.get(strategy)
