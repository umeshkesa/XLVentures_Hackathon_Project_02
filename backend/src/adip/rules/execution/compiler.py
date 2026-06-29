"""RuleCompiler — compiles parsed rules into CompiledRule.

Converts parsed Rule objects into an optimised internal
representation (CompiledRule) with compiled conditions, actions,
cached metadata, and version tracking.
"""

from __future__ import annotations

import structlog

from adip.rules.contracts.models import Rule
from adip.rules.execution.models import CompiledRule

log = structlog.get_logger(__name__)


class RuleCompiler:
    """Compiles rules into an optimised representation for evaluation."""

    def compile(self, rule: Rule) -> CompiledRule:
        """Compile a rule into a CompiledRule.

        Placeholder — copies rule conditions/actions into serialisable
        dict form for structural preparation.
        """
        rule_id = str(rule.rule_id)
        log.info("rule_compiler.compile", rule_id=rule_id, version=rule.version)

        compiled_conditions = [
            {
                "condition_id": str(c.condition_id),
                "field": c.field,
                "operator": c.operator,
                "value": c.value,
                "logic": c.logic,
            }
            for c in rule.conditions
        ]

        compiled_actions = [
            {
                "action_id": str(a.action_id),
                "action_type": a.action_type,
                "parameters": dict(a.parameters),
                "priority": a.priority,
            }
            for a in rule.actions
        ]

        return CompiledRule(
            rule_id=rule.rule_id,
            rule=rule,
            compiled_conditions=compiled_conditions,
            compiled_actions=compiled_actions,
            metadata={
                "condition_count": len(compiled_conditions),
                "action_count": len(compiled_actions),
                "compiled": True,
            },
            version=rule.version,
        )

    def compile_batch(self, rules: list[Rule]) -> list[CompiledRule]:
        """Compile multiple rules."""
        log.info("rule_compiler.compile_batch", count=len(rules))
        return [self.compile(r) for r in rules]

    def validate_compiled(self, compiled: CompiledRule) -> list[str]:
        """Validate a compiled rule. Returns violations (empty = valid)."""
        violations: list[str] = []
        rule_id = str(compiled.rule_id)
        log.info("rule_compiler.validate_compiled", rule_id=rule_id)

        if compiled.version < 1:
            violations.append(f"Compiled rule version must be >= 1, got {compiled.version}")

        return violations

    def optimize(self, compiled: CompiledRule) -> CompiledRule:
        """Optimize a compiled rule.

        Placeholder — returns the same compiled rule with an
        optimisation marker in metadata.
        """
        rule_id = str(compiled.rule_id)
        log.info("rule_compiler.optimize", rule_id=rule_id)
        meta = dict(compiled.metadata)
        meta["optimized"] = True
        meta["optimizations_applied"] = ["none (placeholder)"]
        return compiled.model_copy(update={"metadata": meta})
