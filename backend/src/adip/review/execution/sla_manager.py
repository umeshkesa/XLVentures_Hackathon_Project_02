"""ReviewSLAManager — SLA tracking and breach detection for reviews.

Manages SLA records per review, computes remaining time, detects
breaches based on elapsed time since start, and supports optional
auto-escalation callbacks.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

import structlog

from adip.review.execution.models import SLARecord

log = structlog.get_logger(__name__)


class ReviewSLAManager:
    """In-memory SLA manager for review operations."""

    def __init__(self) -> None:
        self._sla_records: dict[str, SLARecord] = {}
        self._breach_callbacks: list[Callable[[SLARecord], None]] = []

    def start_sla(
        self,
        review_id: str,
        sla_minutes: int = 60,
        auto_escalate: bool = False,
        correlation_id: str = "",
    ) -> SLARecord:
        """Start SLA tracking for a review."""
        now = datetime.now(UTC)
        record = SLARecord(
            review_id=review_id,
            sla_minutes=sla_minutes,
            remaining_minutes=float(sla_minutes),
            started_at=now,
            deadline_at=None,
            is_breached=False,
            auto_escalate=auto_escalate,
        )
        self._sla_records[review_id] = record
        log.info(
            "sla_manager.start_sla",
            review_id=review_id,
            sla_minutes=sla_minutes,
            correlation_id=correlation_id,
        )
        return record

    def get_remaining_time(self, review_id: str) -> float:
        """Return remaining minutes for an SLA. Returns 0.0 if not found."""
        record = self._sla_records.get(review_id)
        if record is None:
            return 0.0
        elapsed = (datetime.now(UTC) - record.started_at).total_seconds() / 60.0
        remaining = max(0.0, float(record.sla_minutes) - elapsed)
        if remaining != record.remaining_minutes:
            record.remaining_minutes = remaining
        return remaining

    def is_breached(self, review_id: str) -> bool:
        """Check whether an SLA has been breached."""
        record = self._sla_records.get(review_id)
        if record is None:
            return False
        remaining = self.get_remaining_time(review_id)
        breached = remaining <= 0.0
        if breached and not record.is_breached:
            record.is_breached = True
            record.breached_at = datetime.now(UTC)
        return breached

    def check_breaches(self, correlation_id: str = "") -> list[SLARecord]:
        """Check all SLAs for breaches. Returns newly breached records."""
        breached: list[SLARecord] = []
        for review_id, record in self._sla_records.items():
            if self.is_breached(review_id):
                breached.append(record)
                for cb in self._breach_callbacks:
                    cb(record)
        if breached:
            log.info(
                "sla_manager.check_breaches",
                breach_count=len(breached),
                correlation_id=correlation_id,
            )
        return breached

    def get_sla(self, review_id: str) -> SLARecord | None:
        """Retrieve an SLA record by review ID."""
        return self._sla_records.get(review_id)

    def update_sla_minutes(self, review_id: str, sla_minutes: int) -> bool:
        """Update the SLA duration for a review. Returns False if not found."""
        record = self._sla_records.get(review_id)
        if record is None:
            return False
        elapsed = (datetime.now(UTC) - record.started_at).total_seconds() / 60.0
        record.sla_minutes = sla_minutes
        record.remaining_minutes = max(0.0, float(sla_minutes) - elapsed)
        log.info(
            "sla_manager.update_sla_minutes",
            review_id=review_id,
            sla_minutes=sla_minutes,
        )
        return True

    def get_all_slas(self) -> list[SLARecord]:
        """Return all SLA records."""
        return list(self._sla_records.values())

    def clear(self) -> None:
        """Clear all SLA records and callbacks."""
        self._sla_records.clear()
        self._breach_callbacks.clear()
        log.info("sla_manager.clear")
