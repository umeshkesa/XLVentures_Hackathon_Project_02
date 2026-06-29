"""Tests for Rule Manager interfaces."""

from __future__ import annotations

import abc

from adip.rules.enums import (
    EvaluationStrategyType,
)
from adip.rules.interfaces import (
    CompositeEvaluation,
    ConditionalEvaluation,
    ConflictResolver,
    EvaluationStrategy,
    PriorityEngine,
    PriorityEvaluation,
    RuleCache,
    RuleCompiler,
    RuleCoordinator,
    RuleEvaluator,
    RuleManager,
    RuleParser,
    RuleService,
    RuleValidator,
    SequentialEvaluation,
)


class TestInterfacesAreAbstract:
    def test_rule_service_is_abstract(self) -> None:
        assert issubclass(RuleService, abc.ABC)

    def test_rule_manager_is_abstract(self) -> None:
        assert issubclass(RuleManager, abc.ABC)

    def test_rule_coordinator_is_abstract(self) -> None:
        assert issubclass(RuleCoordinator, abc.ABC)

    def test_rule_validator_is_abstract(self) -> None:
        assert issubclass(RuleValidator, abc.ABC)

    def test_rule_parser_is_abstract(self) -> None:
        assert issubclass(RuleParser, abc.ABC)

    def test_rule_compiler_is_abstract(self) -> None:
        assert issubclass(RuleCompiler, abc.ABC)

    def test_rule_evaluator_is_abstract(self) -> None:
        assert issubclass(RuleEvaluator, abc.ABC)

    def test_conflict_resolver_is_abstract(self) -> None:
        assert issubclass(ConflictResolver, abc.ABC)

    def test_priority_engine_is_abstract(self) -> None:
        assert issubclass(PriorityEngine, abc.ABC)

    def test_rule_cache_is_abstract(self) -> None:
        assert issubclass(RuleCache, abc.ABC)

    def test_evaluation_strategy_is_abstract(self) -> None:
        assert issubclass(EvaluationStrategy, abc.ABC)


class TestConcreteStrategies:
    def test_sequential_evaluation(self) -> None:
        strategy = SequentialEvaluation()
        assert strategy.get_strategy_type() == EvaluationStrategyType.SEQUENTIAL
        assert hasattr(strategy, "evaluate")

    def test_priority_evaluation(self) -> None:
        strategy = PriorityEvaluation()
        assert strategy.get_strategy_type() == EvaluationStrategyType.PRIORITY
        assert hasattr(strategy, "evaluate")

    def test_conditional_evaluation(self) -> None:
        strategy = ConditionalEvaluation()
        assert strategy.get_strategy_type() == EvaluationStrategyType.CONDITIONAL
        assert hasattr(strategy, "evaluate")

    def test_composite_evaluation(self) -> None:
        strategy = CompositeEvaluation()
        assert strategy.get_strategy_type() == EvaluationStrategyType.COMPOSITE
        assert hasattr(strategy, "evaluate")


class TestInterfaceMethods:
    def test_rule_service_methods(self) -> None:
        """Verify RuleService declares all required methods."""
        methods = [
            "create_rule", "get_rule", "update_rule", "delete_rule",
            "evaluate", "create_ruleset", "get_ruleset",
            "activate_rule", "archive_rule", "health", "get_metrics",
        ]
        for method in methods:
            assert hasattr(RuleService, method)
            assert getattr(RuleService, method).__isabstractmethod__

    def test_rule_manager_methods(self) -> None:
        """Verify RuleManager declares all required methods."""
        methods = [
            "create_rule", "read_rule", "update_rule", "delete_rule",
            "search_rules", "evaluate_rules", "create_ruleset",
            "read_ruleset", "update_ruleset", "delete_ruleset",
            "activate_rule", "archive_rule", "get_health", "get_metrics",
        ]
        for method in methods:
            assert hasattr(RuleManager, method), f"Missing: {method}"
            assert getattr(RuleManager, method).__isabstractmethod__

    def test_rule_coordinator_methods(self) -> None:
        """Verify RuleCoordinator declares all required methods."""
        methods = [
            "create_rule", "get_rule", "update_rule", "delete_rule",
            "evaluate", "create_ruleset", "get_ruleset", "update_ruleset",
            "delete_ruleset", "activate_rule", "archive_rule",
            "health", "metrics",
        ]
        for method in methods:
            assert hasattr(RuleCoordinator, method), f"Missing: {method}"
            assert getattr(RuleCoordinator, method).__isabstractmethod__

    def test_rule_validator_methods(self) -> None:
        methods = ["validate_rule", "validate_ruleset", "validate_context"]
        for method in methods:
            assert hasattr(RuleValidator, method)
            assert getattr(RuleValidator, method).__isabstractmethod__

    def test_rule_parser_methods(self) -> None:
        methods = ["parse_rule", "parse_ruleset", "get_supported_formats"]
        for method in methods:
            assert hasattr(RuleParser, method)
            assert getattr(RuleParser, method).__isabstractmethod__

    def test_rule_compiler_methods(self) -> None:
        methods = ["compile_rule", "compile_ruleset"]
        for method in methods:
            assert hasattr(RuleCompiler, method)
            assert getattr(RuleCompiler, method).__isabstractmethod__

    def test_rule_evaluator_methods(self) -> None:
        methods = ["evaluate_rule", "evaluate_ruleset", "get_supported_strategies"]
        for method in methods:
            assert hasattr(RuleEvaluator, method)
            assert getattr(RuleEvaluator, method).__isabstractmethod__

    def test_conflict_resolver_methods(self) -> None:
        methods = ["detect_conflicts", "resolve_conflicts"]
        for method in methods:
            assert hasattr(ConflictResolver, method)
            assert getattr(ConflictResolver, method).__isabstractmethod__

    def test_priority_engine_methods(self) -> None:
        methods = ["order_rules", "get_effective_priority"]
        for method in methods:
            assert hasattr(PriorityEngine, method)
            assert getattr(PriorityEngine, method).__isabstractmethod__

    def test_rule_cache_methods(self) -> None:
        methods = ["get", "set", "invalidate", "clear"]
        for method in methods:
            assert hasattr(RuleCache, method)
            assert getattr(RuleCache, method).__isabstractmethod__

    def test_evaluation_strategy_methods(self) -> None:
        methods = ["evaluate", "get_strategy_type"]
        for method in methods:
            assert hasattr(EvaluationStrategy, method)
            assert getattr(EvaluationStrategy, method).__isabstractmethod__
