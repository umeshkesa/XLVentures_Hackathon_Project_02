"""Tests for Rule Manager Phase 2 imports."""

from __future__ import annotations


class TestExecutionImports:
    def test_execution_models_importable(self) -> None:
        from adip.rules.execution.models import (
            CompiledRule,
            ConflictReport,
            VersionRecord,
        )
        assert CompiledRule is not None
        assert ConflictReport is not None
        assert VersionRecord is not None

    def test_execution_components_importable(self) -> None:
        from adip.rules.execution.cache import RuleCache
        from adip.rules.execution.compiler import RuleCompiler
        from adip.rules.execution.conflict_resolver import ConflictResolver
        from adip.rules.execution.evaluator import RuleEvaluator
        from adip.rules.execution.lifecycle import RuleLifecycleManager
        from adip.rules.execution.metrics import RuleMetricsCollector
        from adip.rules.execution.parser import RuleParser
        from adip.rules.execution.policy import RulePolicyEngine
        from adip.rules.execution.priority_engine import PriorityEngine
        from adip.rules.execution.strategies import (
            CompositeEvaluationStrategy,
            ConditionalEvaluationStrategy,
            EvaluationStrategy,
            PriorityEvaluationStrategy,
            SequentialEvaluationStrategy,
            get_strategy,
        )
        from adip.rules.execution.trace import RuleTrace
        from adip.rules.execution.validator import RuleValidator
        from adip.rules.execution.version_manager import RuleVersionManager
        assert RuleValidator is not None
        assert RuleParser is not None
        assert RuleCompiler is not None
        assert RuleVersionManager is not None
        assert RuleLifecycleManager is not None
        assert RuleEvaluator is not None
        assert EvaluationStrategy is not None
        assert SequentialEvaluationStrategy is not None
        assert PriorityEvaluationStrategy is not None
        assert ConditionalEvaluationStrategy is not None
        assert CompositeEvaluationStrategy is not None
        assert get_strategy is not None
        assert ConflictResolver is not None
        assert PriorityEngine is not None
        assert RuleCache is not None
        assert RulePolicyEngine is not None
        assert RuleTrace is not None
        assert RuleMetricsCollector is not None

    def test_top_level_exports_include_execution(self) -> None:
        from adip.rules import (
            CompiledRule,
            ConflictResolver,
            RuleCache,
            RuleLifecycleManager,
        )
        assert CompiledRule is not None
        assert ConflictResolver is not None
        assert RuleCache is not None
        assert RuleLifecycleManager is not None

    def test_orchestration_imports_available(self) -> None:
        """Phase 3 orchestration components are importable."""
        from adip.rules.orchestration.confidence import RuleConfidenceCalculator
        from adip.rules.orchestration.coordinator import RuleCoordinator
        from adip.rules.orchestration.manager import RuleManager
        from adip.rules.orchestration.session import RuleSessionManager
        assert RuleCoordinator is not None
        assert RuleManager is not None
        assert RuleSessionManager is not None
        assert RuleConfidenceCalculator is not None
