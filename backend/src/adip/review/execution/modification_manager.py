"""ModificationManager — tracks and manages review decision modifications.

Records approve, reject, modify, request-information, escalate, and
defer actions as ModificationRecord entries for traceability.
"""

from __future__ import annotations

import structlog
from pydantic.types import UUID4

from adip.review.execution.models import ModificationRecord

log = structlog.get_logger(__name__)


class ModificationManager:
    """In-memory store for review decision modification records."""

    def __init__(self) -> None:
        self._modifications: list[ModificationRecord] = []

    def approve(
        self,
        decision_id: UUID4,
        reviewer_id: str = "",
        reason: str = "",
        correlation_id: str = "",
    ) -> ModificationRecord:
        """Record an approval action for a review decision."""
        record = ModificationRecord(
            decision_id=decision_id,
            modification_type="APPROVED",
            previous_value="",
            new_value="approved",
            reason=reason,
            modified_by=reviewer_id,
        )
        self._modifications.append(record)
        log.info(
            "modification_manager.approve",
            decision_id=str(decision_id),
            reviewer_id=reviewer_id,
            correlation_id=correlation_id,
        )
        return record

    def reject(
        self,
        decision_id: UUID4,
        reviewer_id: str = "",
        reason: str = "",
        correlation_id: str = "",
    ) -> ModificationRecord:
        """Record a rejection action for a review decision."""
        record = ModificationRecord(
            decision_id=decision_id,
            modification_type="REJECTED",
            previous_value="",
            new_value="rejected",
            reason=reason,
            modified_by=reviewer_id,
        )
        self._modifications.append(record)
        log.info(
            "modification_manager.reject",
            decision_id=str(decision_id),
            reviewer_id=reviewer_id,
            correlation_id=correlation_id,
        )
        return record

    def modify(
        self,
        decision_id: UUID4,
        reviewer_id: str = "",
        previous_value: str = "",
        new_value: str = "",
        reason: str = "",
        correlation_id: str = "",
    ) -> ModificationRecord:
        """Record a modification action for a review decision."""
        record = ModificationRecord(
            decision_id=decision_id,
            modification_type="MODIFIED",
            previous_value=previous_value,
            new_value=new_value,
            reason=reason,
            modified_by=reviewer_id,
        )
        self._modifications.append(record)
        log.info(
            "modification_manager.modify",
            decision_id=str(decision_id),
            reviewer_id=reviewer_id,
            correlation_id=correlation_id,
        )
        return record

    def request_information(
        self,
        decision_id: UUID4,
        reviewer_id: str = "",
        reason: str = "",
        correlation_id: str = "",
    ) -> ModificationRecord:
        """Record an information request for a review decision."""
        record = ModificationRecord(
            decision_id=decision_id,
            modification_type="MORE_INFORMATION_REQUIRED",
            previous_value="",
            new_value="more_information_required",
            reason=reason,
            modified_by=reviewer_id,
        )
        self._modifications.append(record)
        log.info(
            "modification_manager.request_information",
            decision_id=str(decision_id),
            reviewer_id=reviewer_id,
            correlation_id=correlation_id,
        )
        return record

    def escalate(
        self,
        decision_id: UUID4,
        reviewer_id: str = "",
        reason: str = "",
        correlation_id: str = "",
    ) -> ModificationRecord:
        """Record an escalation action for a review decision."""
        record = ModificationRecord(
            decision_id=decision_id,
            modification_type="ESCALATED",
            previous_value="",
            new_value="escalated",
            reason=reason,
            modified_by=reviewer_id,
        )
        self._modifications.append(record)
        log.info(
            "modification_manager.escalate",
            decision_id=str(decision_id),
            reviewer_id=reviewer_id,
            correlation_id=correlation_id,
        )
        return record

    def defer(
        self,
        decision_id: UUID4,
        reviewer_id: str = "",
        reason: str = "",
        correlation_id: str = "",
    ) -> ModificationRecord:
        """Record a deferral action for a review decision."""
        record = ModificationRecord(
            decision_id=decision_id,
            modification_type="DEFERRED",
            previous_value="",
            new_value="deferred",
            reason=reason,
            modified_by=reviewer_id,
        )
        self._modifications.append(record)
        log.info(
            "modification_manager.defer",
            decision_id=str(decision_id),
            reviewer_id=reviewer_id,
            correlation_id=correlation_id,
        )
        return record

    def get_modifications(self, decision_id: UUID4) -> list[ModificationRecord]:
        """Return all modification records for a given decision."""
        result = [
            m for m in self._modifications if m.decision_id == decision_id
        ]
        log.info(
            "modification_manager.get_modifications",
            decision_id=str(decision_id),
            count=len(result),
        )
        return result

    def get_modifications_by_type(self, modification_type: str) -> list[ModificationRecord]:
        """Return all modification records matching a given type."""
        result = [
            m for m in self._modifications if m.modification_type == modification_type
        ]
        log.info(
            "modification_manager.get_modifications_by_type",
            modification_type=modification_type,
            count=len(result),
        )
        return result

    def clear(self) -> None:
        """Remove all stored modification records."""
        count = len(self._modifications)
        self._modifications.clear()
        log.info("modification_manager.clear", cleared=count)
