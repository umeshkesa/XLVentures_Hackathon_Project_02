"""ConflictResolver — detects and resolves conflicts between rules.

Identifies rule conflicts such as direct overlap, priority
inversion, and circular dependencies, and applies the configured
resolution strategy.
"""

from __future__ import annotations

import structlog

from adip.rules.contracts.models import Rule, RuleDecision
from adip.rules.execution.models import ConflictReport

log = structlog.get_logger(__name__)


class ConflictResolver:
    """Detects and resolves conflicts between rules."""

    def detect_conflicts(self, rules: list[Rule]) -> list[ConflictReport]:
        """Detect conflicts within a list of rules.

        Placeholder — checks for basic direct overlap by name.
        """
        log.info("conflict_resolver.detect_conflicts", rule_count=len(rules))
        reports: list[ConflictReport] = []

        for i, a in enumerate(rules):
            for j, b in enumerate(rules):
                if i >= j:
                    continue
                if a.name and b.name and a.name == b.name:
                    reports.append(ConflictReport(
                        rule_id=a.rule_id,
                        conflicting_rule_id=b.rule_id,
                        conflict_type="direct_overlap",
                        description=f"Rules share the same name: '{a.name}'",
                        resolution="PRIORITY",
                        resolved_by="ConflictResolver",
                    ))

        return reports

    def resolve_conflicts(
        self,
        decisions: list[RuleDecision],
        strategy: str = "PRIORITY",
    ) -> list[RuleDecision]:
        """Resolve conflicts between decisions using the given strategy.

        Placeholder — returns decisions sorted by confidence descending.
        """
        log.info("conflict_resolver.resolve_conflicts", decision_count=len(decisions), strategy=strategy)

        if strategy == "PRIORITY":
            return sorted(decisions, key=lambda d: d.confidence, reverse=True)
        elif strategy == "DENY_OVERRIDE":
            deny = [d for d in decisions if d.decision == "deny"]
            allow = [d for d in decisions if d.decision != "deny"]
            return deny + allow
        else:
            return list(decisions)
