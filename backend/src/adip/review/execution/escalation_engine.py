"""EscalationEngine — deterministic escalation detection and management.

Evaluates review conditions against escalation rules, creates escalation
records, and tracks active/resolved escalations for the Decision Review Layer.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog

from adip.review.execution.models import EscalationRecord

log = structlog.get_logger(__name__)


class EscalationEngine:
    """In-memory escalation engine for review operations."""

    def __init__(self) -> None:
        self._escalations: list[EscalationRecord] = []
        self._escalation_rules: dict[str, dict[str, Any]] = {}

    def add_rule(
        self,
        rule_id: str,
        rule_type: str,
        trigger_role: str,
        target_role: str,
        severity: str,
        max_duration_minutes: int = 0,
        is_active: bool = True,
    ) -> None:
        """Register an escalation rule."""
        self._escalation_rules[rule_id] = {
            "rule_id": rule_id,
            "rule_type": rule_type,
            "trigger_role": trigger_role,
            "target_role": target_role,
            "severity": severity,
            "max_duration_minutes": max_duration_minutes,
            "is_active": is_active,
        }
        log.info("escalation_engine.add_rule", rule_id=rule_id, severity=severity)

    def check_escalation(
        self,
        review_id: str,
        confidence: float,
        risk: str,
        timeout_hours: int = 0,
        criticality: str = "",
        correlation_id: str = "",
    ) -> dict[str, Any]:
        """Deterministic escalation check.

        Triggers escalation if:
        - confidence < 0.3 (LOW confidence)
        - risk == "HIGH"
        - timeout_hours > 0 (TIMEOUT)
        - criticality == "CRITICAL"
        """
        should_escalate = False
        reason = ""
        escalation_type = ""
        target_role = ""
        severity = "MEDIUM"

        if confidence < 0.3:
            should_escalate = True
            reason = "Low confidence score"
            escalation_type = "LOW_CONFIDENCE"
            severity = "HIGH"

        if risk == "HIGH":
            should_escalate = True
            reason = "High risk assessment"
            escalation_type = "HIGH_RISK"
            severity = "HIGH"

        if timeout_hours > 0:
            should_escalate = True
            reason = f"Review timeout exceeded ({timeout_hours}h)"
            escalation_type = "TIMEOUT"
            severity = "MEDIUM"

        if criticality == "CRITICAL":
            should_escalate = True
            reason = "Critical review"
            escalation_type = "CRITICALITY"
            severity = "HIGH"

        result = {
            "should_escalate": should_escalate,
            "reason": reason,
            "escalation_type": escalation_type,
            "target_role": target_role,
            "severity": severity,
        }
        log.info(
            "escalation_engine.check_escalation",
            review_id=review_id,
            should_escalate=should_escalate,
            escalation_type=escalation_type,
            correlation_id=correlation_id,
        )
        return result

    def escalate(
        self,
        review_id: str,
        reason: str,
        escalation_type: str,
        triggered_by: str = "",
        from_role: str = "",
        to_role: str = "",
        severity: str = "MEDIUM",
        correlation_id: str = "",
    ) -> EscalationRecord:
        """Create an escalation record."""
        record = EscalationRecord(
            review_id=review_id,
            reason=reason,
            escalation_type=escalation_type,
            triggered_by=triggered_by,
            from_role=from_role,
            to_role=to_role,
            severity=severity,
        )
        self._escalations.append(record)
        log.info(
            "escalation_engine.escalate",
            escalation_id=str(record.escalation_id),
            review_id=review_id,
            severity=severity,
            correlation_id=correlation_id,
        )
        return record

    def resolve_escalation(self, escalation_id: str, correlation_id: str = "") -> bool:
        """Mark an escalation as resolved."""
        for record in self._escalations:
            if str(record.escalation_id) == escalation_id and not record.resolved:
                record.resolved = True
                record.resolved_at = datetime.now(UTC)
                log.info(
                    "escalation_engine.resolve_escalation",
                    escalation_id=escalation_id,
                    correlation_id=correlation_id,
                )
                return True
        log.warning(
            "escalation_engine.resolve_escalation.not_found",
            escalation_id=escalation_id,
            correlation_id=correlation_id,
        )
        return False

    def get_active_escalations(self) -> list[EscalationRecord]:
        """Return all unresolved escalations."""
        return [e for e in self._escalations if not e.resolved]

    def get_escalations_by_review(self, review_id: str) -> list[EscalationRecord]:
        """Return all escalations for a specific review."""
        return [e for e in self._escalations if e.review_id == review_id]

    def remove_rule(self, rule_id: str) -> bool:
        """Remove an escalation rule by ID."""
        if rule_id in self._escalation_rules:
            del self._escalation_rules[rule_id]
            log.info("escalation_engine.remove_rule", rule_id=rule_id)
            return True
        return False

    def clear(self) -> None:
        """Clear all escalation records and rules."""
        self._escalations.clear()
        self._escalation_rules.clear()
        log.info("escalation_engine.clear")
