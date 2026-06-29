"""ReviewChecklist — checklist management for review operations.

Manages review completion checklists with mandatory items,
custom items, completion tracking, and summary reporting.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.review.execution.models import ChecklistItem

log = structlog.get_logger(__name__)

_DEFAULT_ITEMS: list[dict[str, Any]] = [
    {"item_name": "Evidence Reviewed", "description": "All evidence has been reviewed and verified"},
    {"item_name": "Explanation Reviewed", "description": "Explanation has been reviewed and understood"},
    {"item_name": "Policies Reviewed", "description": "Applicable policies have been reviewed"},
    {"item_name": "Risk Reviewed", "description": "Risk assessment has been reviewed"},
    {"item_name": "Recommendation Reviewed", "description": "Recommendation has been reviewed"},
]


class ReviewChecklist:
    """In-memory checklist manager for review operations."""

    def __init__(self) -> None:
        self._checklists: dict[str, list[ChecklistItem]] = {}

    def initialize_checklist(
        self,
        review_id: str,
        correlation_id: str = "",
    ) -> list[ChecklistItem]:
        """Create a standard checklist for a review with default items."""
        items = [
            ChecklistItem(
                review_id=review_id,
                item_name=entry["item_name"],
                description=entry["description"],
                is_complete=False,
                required=True,
            )
            for entry in _DEFAULT_ITEMS
        ]
        self._checklists[review_id] = items
        log.info(
            "review_checklist.initialized",
            review_id=review_id,
            item_count=len(items),
            correlation_id=correlation_id,
        )
        return list(items)

    def complete_item(
        self,
        review_id: str,
        item_name: str,
        completed_by: str = "",
        correlation_id: str = "",
    ) -> bool:
        """Mark a checklist item as complete. Returns False if item not found."""
        items = self._checklists.get(review_id)
        if items is None:
            log.warning("review_checklist.review_not_found", review_id=review_id)
            return False
        for item in items:
            if item.item_name == item_name and not item.is_complete:
                item.is_complete = True
                item.completed_by = completed_by
                item.completed_at = datetime.now(UTC)
                log.info(
                    "review_checklist.item_completed",
                    review_id=review_id,
                    item_name=item_name,
                    completed_by=completed_by,
                    correlation_id=correlation_id,
                )
                return True
        log.warning(
            "review_checklist.item_not_found_or_already_done",
            review_id=review_id,
            item_name=item_name,
        )
        return False

    def is_item_complete(self, review_id: str, item_name: str) -> bool:
        """Check if a specific checklist item is complete."""
        items = self._checklists.get(review_id)
        if items is None:
            return False
        return any(
            item.item_name == item_name and item.is_complete
            for item in items
        )

    def is_checklist_complete(self, review_id: str) -> bool:
        """Check if all required items in the checklist are complete."""
        items = self._checklists.get(review_id)
        if items is None:
            return False
        return all(
            item.is_complete if item.required else True
            for item in items
        )

    def get_checklist(self, review_id: str) -> list[ChecklistItem]:
        """Get the full checklist for a review."""
        return list(self._checklists.get(review_id, []))

    def get_summary(self, review_id: str) -> dict[str, Any]:
        """Get a summary of checklist progress."""
        items = self._checklists.get(review_id, [])
        total = len(items)
        completed = sum(1 for i in items if i.is_complete)
        pending = total - completed
        complete = total > 0 and all(
            i.is_complete if i.required else True
            for i in items
        )
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "complete": complete,
        }

    def add_custom_item(
        self,
        review_id: str,
        item_name: str,
        description: str = "",
        required: bool = True,
    ) -> ChecklistItem:
        """Add a custom item to a review's checklist."""
        items = self._checklists.get(review_id)
        if items is None:
            items = []
            self._checklists[review_id] = items
        item = ChecklistItem(
            review_id=review_id,
            item_name=item_name,
            description=description,
            is_complete=False,
            required=required,
        )
        items.append(item)
        log.info(
            "review_checklist.custom_item_added",
            review_id=review_id,
            item_name=item_name,
            required=required,
        )
        return item

    def remove_item(self, review_id: str, item_name: str) -> bool:
        """Remove a custom item from a review's checklist. Can't remove required defaults."""
        items = self._checklists.get(review_id)
        if items is None:
            return False
        for i, item in enumerate(items):
            if item.item_name == item_name and not item.required:
                items.pop(i)
                log.info(
                    "review_checklist.item_removed",
                    review_id=review_id,
                    item_name=item_name,
                )
                return True
        log.warning(
            "review_checklist.item_not_removed",
            review_id=review_id,
            item_name=item_name,
        )
        return False

    def clear(self) -> None:
        """Clear all checklists."""
        count = sum(len(v) for v in self._checklists.values())
        self._checklists.clear()
        log.info("review_checklist.clear", cleared=count)
