"""RuleLifecycleManager — manages rule lifecycle transitions.

Validates lifecycle transitions according to allowed state machine
rules and tracks lifecycle history for audit and observability.
"""

from __future__ import annotations

import structlog

from adip.rules.contracts.models import Rule
from adip.rules.enums import RuleLifecycleStatus
from adip.rules.execution.models import LifecycleHistoryEntry

log = structlog.get_logger(__name__)


_ALLOWED_TRANSITIONS: dict[RuleLifecycleStatus, set[RuleLifecycleStatus]] = {
    RuleLifecycleStatus.DRAFT: {RuleLifecycleStatus.UNDER_REVIEW},
    RuleLifecycleStatus.UNDER_REVIEW: {RuleLifecycleStatus.APPROVED, RuleLifecycleStatus.DRAFT},
    RuleLifecycleStatus.APPROVED: {RuleLifecycleStatus.ACTIVE, RuleLifecycleStatus.DRAFT},
    RuleLifecycleStatus.ACTIVE: {RuleLifecycleStatus.DEPRECATED, RuleLifecycleStatus.ARCHIVED},
    RuleLifecycleStatus.DEPRECATED: {RuleLifecycleStatus.ARCHIVED},
    RuleLifecycleStatus.ARCHIVED: set(),
}


class RuleLifecycleManager:
    """Manages rule lifecycle transitions."""

    def __init__(self) -> None:
        self._history: list[LifecycleHistoryEntry] = []

    def get_current_status(self, rule: Rule) -> RuleLifecycleStatus:
        """Return the current lifecycle status of a rule."""
        return rule.status

    def transition(
        self,
        rule: Rule,
        to_status: RuleLifecycleStatus,
        reason: str = "",
        changed_by: str = "",
    ) -> Rule:
        """Transition a rule to a new lifecycle status.

        Validates the transition before applying. Returns an updated
        rule with the new status.
        """
        rule_id = str(rule.rule_id)
        from_status = rule.status

        log.info(
            "rule_lifecycle.transition",
            rule_id=rule_id,
            from_status=from_status.value,
            to_status=to_status.value,
        )

        if to_status == from_status:
            return rule

        allowed = _ALLOWED_TRANSITIONS.get(from_status, set())
        if to_status not in allowed:
            raise ValueError(
                f"Illegal lifecycle transition: {from_status.value} -> {to_status.value} "
                f"for rule {rule_id}"
            )

        entry = LifecycleHistoryEntry(
            rule_id=rule.rule_id,
            from_status=from_status,
            to_status=to_status,
            reason=reason or f"Transitioned from {from_status.value} to {to_status.value}",
            changed_by=changed_by,
        )
        self._history.append(entry)

        result = rule.model_copy(update={"status": to_status, "updated_at": entry.timestamp})
        log.info("rule_lifecycle.transition.complete", rule_id=rule_id, to_status=to_status.value)
        return result

    def get_history(self, rule_id: str) -> list[LifecycleHistoryEntry]:
        """Return lifecycle history for a specific rule."""
        return [e for e in self._history if str(e.rule_id) == rule_id]

    def get_all_history(self) -> list[LifecycleHistoryEntry]:
        """Return all lifecycle history entries."""
        return list(self._history)

    def clear(self) -> None:
        """Clear all lifecycle history."""
        self._history.clear()
