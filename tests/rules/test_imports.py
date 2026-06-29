"""Tests for Rule Manager package imports and re-exports."""

from __future__ import annotations


class TestTopLevelImports:
    def test_all_imports(self) -> None:
        from adip.rules import (  # noqa: F811
            AbstractRuleService,
            Rule,
            RuleCreated,
            RuleDomain,
            RuleException,
            RuleRequestDTO,
        )
        assert RuleDomain is not None
        assert Rule is not None
        assert AbstractRuleService is not None
        assert RuleCreated is not None
        assert RuleException is not None
        assert RuleRequestDTO is not None

    def test_enums_importable(self) -> None:
        from adip.rules.enums import (
            RuleDomain,
        )
        assert RuleDomain.SYSTEM == "SYSTEM"

    def test_models_importable(self) -> None:
        from adip.rules.contracts.models import (
            Rule,
            RuleConfidence,
            RuleDecision,
            RuleExplainabilityMetadata,
            RuleSet,
        )
        assert Rule is not None
        assert RuleSet is not None
        assert RuleDecision is not None
        assert RuleConfidence is not None
        assert RuleExplainabilityMetadata is not None

    def test_events_importable(self) -> None:
        from adip.rules.contracts.events import (
            RuleCreated,
            RuleUpdated,
        )
        assert RuleCreated is not None
        assert RuleUpdated is not None

    def test_dtos_importable(self) -> None:
        from adip.rules.dtos import RuleRequestDTO
        assert RuleRequestDTO is not None

    def test_exceptions_importable(self) -> None:
        from adip.rules.contracts.exceptions import (
            RuleException,
        )
        assert RuleException is not None

    def test_interfaces_importable(self) -> None:
        from adip.rules.interfaces import (
            RuleCoordinator as AbstractRuleCoordinator,
        )
        from adip.rules.interfaces import (
            RuleManager as AbstractRuleManager,
        )
        from adip.rules.interfaces import (
            RuleService as AbstractRuleService,
        )
        assert AbstractRuleService is not None
        assert AbstractRuleManager is not None
        assert AbstractRuleCoordinator is not None

class TestAllNames:
    def test_all_names_in_all(self) -> None:
        from adip.rules import __all__ as top_all
        expected = {
            "RuleDomain", "RuleType", "RuleLifecycleStatus", "EvaluationStrategyType",
            "Rule", "RuleSet", "RuleCondition", "RuleAction", "RuleContext",
            "RuleDecision", "RuleEvaluation", "RulePolicy", "RuleHealth", "RuleMetrics",
            "RuleSession", "RuleConfidence", "RuleExplainabilityMetadata",
            "RuleRequestDTO", "RuleResponseDTO", "RuleEvaluationDTO",
            "EventVersion", "RuleEvent", "RuleCreated", "RuleUpdated",
            "RuleActivated", "RuleEvaluated", "RuleConflictDetected", "RuleArchived",
            "RuleException", "RuleValidationException", "RuleConflictException",
            "RuleEvaluationException",
            "AbstractRuleService", "AbstractRuleManager", "AbstractRuleCoordinator",
            "AbstractRuleValidator", "AbstractRuleParser", "AbstractRuleCompiler",
            "AbstractRuleEvaluator", "AbstractConflictResolver", "AbstractPriorityEngine",
            "AbstractRuleCache", "AbstractEvaluationStrategy",
            "AbstractSequentialEvaluation", "AbstractPriorityEvaluation",
            "AbstractConditionalEvaluation", "AbstractCompositeEvaluation",
            "CompiledRule", "ConflictReport", "LifecycleHistoryEntry", "TraceRecord",
            "VersionRecord",
            "RuleValidator", "RuleParser", "RuleCompiler",
            "RuleVersionManager", "RuleLifecycleManager",
            "RuleEvaluator", "EvaluationStrategy",
            "SequentialEvaluationStrategy", "PriorityEvaluationStrategy",
            "ConditionalEvaluationStrategy", "CompositeEvaluationStrategy",
            "get_strategy",
            "ConflictResolver", "PriorityEngine", "RuleCache",
            "RulePolicyEngine", "RuleTrace", "RuleMetricsCollector",
        }
        assert set(top_all) == expected
