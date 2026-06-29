"""Tests for RuleCompiler."""

from __future__ import annotations

from adip.rules.contracts.models import Rule, RuleAction, RuleCondition
from adip.rules.enums import RuleType
from adip.rules.execution.compiler import RuleCompiler
from adip.rules.execution.models import CompiledRule


class TestRuleCompiler:
    def test_compile_returns_compiled_rule(self) -> None:
        rule = Rule(name="Test", rule_type=RuleType.BUSINESS)
        compiler = RuleCompiler()
        result = compiler.compile(rule)
        assert isinstance(result, CompiledRule)
        assert result.version == 1

    def test_compile_with_conditions(self) -> None:
        rule = Rule(
            name="Test",
            conditions=[RuleCondition(field="temp", operator="gt", value="100")],
        )
        compiler = RuleCompiler()
        result = compiler.compile(rule)
        assert len(result.compiled_conditions) == 1
        assert result.compiled_conditions[0]["field"] == "temp"

    def test_compile_with_actions(self) -> None:
        rule = Rule(
            name="Test",
            actions=[RuleAction(action_type="alert", parameters={"channel": "slack"})],
        )
        compiler = RuleCompiler()
        result = compiler.compile(rule)
        assert len(result.compiled_actions) == 1
        assert result.compiled_actions[0]["action_type"] == "alert"

    def test_compile_batch(self) -> None:
        rules = [
            Rule(name="R1"),
            Rule(name="R2"),
            Rule(name="R3"),
        ]
        compiler = RuleCompiler()
        results = compiler.compile_batch(rules)
        assert len(results) == 3
        assert all(isinstance(r, CompiledRule) for r in results)

    def test_validate_compiled_valid(self) -> None:
        rule = Rule(name="Test")
        compiler = RuleCompiler()
        compiled = compiler.compile(rule)
        violations = compiler.validate_compiled(compiled)
        assert violations == []

    def test_validate_compiled_invalid_version(self) -> None:
        rule = Rule(name="Test")
        compiler = RuleCompiler()
        compiled = compiler.compile(rule)
        bad = compiled.model_copy(update={"version": 0})
        violations = compiler.validate_compiled(bad)
        assert len(violations) > 0

    def test_optimize(self) -> None:
        rule = Rule(name="Test")
        compiler = RuleCompiler()
        compiled = compiler.compile(rule)
        optimized = compiler.optimize(compiled)
        assert optimized.metadata.get("optimized") is True
