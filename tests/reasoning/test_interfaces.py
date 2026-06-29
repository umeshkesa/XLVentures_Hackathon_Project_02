"""Tests for Reasoning Engine interfaces.

Verifies all abstract interfaces are properly defined,
cannot be instantiated directly, and declare the required
abstract methods.
"""

from __future__ import annotations

import pytest

from adip.reasoning.interfaces import (
    ContradictionDetector,
    HypothesisGenerator,
    InferenceEngine,
    ReasoningCoordinator,
    ReasoningManager,
    ReasoningPathBuilder,
    ReasoningService,
    ReasoningStrategy,
    ReasoningValidator,
)


class TestInterfaces:
    def test_reasoning_service_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            ReasoningService()  # type: ignore[abstract]

    def test_reasoning_manager_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            ReasoningManager()  # type: ignore[abstract]

    def test_reasoning_coordinator_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            ReasoningCoordinator()  # type: ignore[abstract]

    def test_reasoning_strategy_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            ReasoningStrategy()  # type: ignore[abstract]

    def test_hypothesis_generator_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            HypothesisGenerator()  # type: ignore[abstract]

    def test_inference_engine_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            InferenceEngine()  # type: ignore[abstract]

    def test_contradiction_detector_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            ContradictionDetector()  # type: ignore[abstract]

    def test_reasoning_validator_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            ReasoningValidator()  # type: ignore[abstract]

    def test_reasoning_path_builder_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            ReasoningPathBuilder()  # type: ignore[abstract]


class TestInterfaceMethods:
    def test_reasoning_service_has_abstract_methods(self) -> None:
        methods = {
            "reason",
            "get_result",
            "get_health",
            "get_metrics",
        }
        for m in methods:
            assert hasattr(ReasoningService, m)
            assert getattr(ReasoningService, m).__isabstractmethod__

    def test_reasoning_manager_has_abstract_methods(self) -> None:
        methods = {
            "execute_reasoning",
            "get_result",
            "get_health",
            "get_metrics",
        }
        for m in methods:
            assert hasattr(ReasoningManager, m)
            assert getattr(ReasoningManager, m).__isabstractmethod__

    def test_reasoning_coordinator_has_abstract_methods(self) -> None:
        methods = {
            "reason",
            "get_result",
            "health",
            "metrics",
        }
        for m in methods:
            assert hasattr(ReasoningCoordinator, m)
            assert getattr(ReasoningCoordinator, m).__isabstractmethod__

    def test_reasoning_strategy_has_abstract_methods(self) -> None:
        methods = {
            "execute",
            "get_strategy_type",
        }
        for m in methods:
            assert hasattr(ReasoningStrategy, m)
            assert getattr(ReasoningStrategy, m).__isabstractmethod__

    def test_hypothesis_generator_has_abstract_methods(self) -> None:
        methods = {
            "generate",
            "validate",
        }
        for m in methods:
            assert hasattr(HypothesisGenerator, m)
            assert getattr(HypothesisGenerator, m).__isabstractmethod__

    def test_inference_engine_has_abstract_methods(self) -> None:
        methods = {
            "infer",
            "chain",
        }
        for m in methods:
            assert hasattr(InferenceEngine, m)
            assert getattr(InferenceEngine, m).__isabstractmethod__

    def test_contradiction_detector_has_abstract_methods(self) -> None:
        methods = {
            "detect",
            "resolve",
        }
        for m in methods:
            assert hasattr(ContradictionDetector, m)
            assert getattr(ContradictionDetector, m).__isabstractmethod__

    def test_reasoning_validator_has_abstract_methods(self) -> None:
        methods = {
            "validate_request",
            "validate_result",
        }
        for m in methods:
            assert hasattr(ReasoningValidator, m)
            assert getattr(ReasoningValidator, m).__isabstractmethod__

    def test_reasoning_path_builder_has_abstract_methods(self) -> None:
        methods = {
            "build_path",
            "add_step",
        }
        for m in methods:
            assert hasattr(ReasoningPathBuilder, m)
            assert getattr(ReasoningPathBuilder, m).__isabstractmethod__
