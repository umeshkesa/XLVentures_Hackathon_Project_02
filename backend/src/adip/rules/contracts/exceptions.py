"""Rule Manager exception hierarchy.

All rule-related exceptions inherit from RuleException to ensure
consistent error handling across the platform.
"""

from __future__ import annotations


class RuleException(Exception):
    """Base exception for all rule errors."""

    def __init__(self, message: str = "Rule error") -> None:
        self.message = message
        super().__init__(self.message)


class RuleValidationException(RuleException):
    """Raised when a rule operation fails validation."""

    def __init__(self, message: str = "Rule validation error") -> None:
        super().__init__(message)


class RuleConflictException(RuleException):
    """Raised when conflicting rules are detected."""

    def __init__(
        self,
        rule_id: str = "",
        conflicting_rule_id: str = "",
        message: str = "",
    ) -> None:
        self.rule_id = rule_id
        self.conflicting_rule_id = conflicting_rule_id
        if not message:
            details = []
            if rule_id:
                details.append(f"rule: {rule_id}")
            if conflicting_rule_id:
                details.append(f"conflicts with: {conflicting_rule_id}")
            message = f"Rule conflict detected ({'; '.join(details)})" if details else "Rule conflict detected"
        super().__init__(message)


class RuleEvaluationException(RuleException):
    """Raised when rule evaluation fails."""

    def __init__(
        self,
        rule_id: str = "",
        context_id: str = "",
        message: str = "",
    ) -> None:
        self.rule_id = rule_id
        self.context_id = context_id
        if not message:
            details = []
            if rule_id:
                details.append(f"rule: {rule_id}")
            if context_id:
                details.append(f"context: {context_id}")
            message = f"Rule evaluation failed ({'; '.join(details)})" if details else "Rule evaluation failed"
        super().__init__(message)
