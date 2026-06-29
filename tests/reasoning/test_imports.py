"""Tests that all Reasoning Engine exports are importable."""

from __future__ import annotations

import adip.reasoning as reasoning


class TestAllExports:
    def test_all_exports_importable(self) -> None:
        for name in reasoning.__all__:
            assert hasattr(reasoning, name), f"{name} not found in reasoning module"


class TestAllNamesMatch:
    def test_all_members_in_all(self) -> None:
        expected = {
            # Enums
            "ReasoningDomain",
            "ReasoningStatus",
            "ReasoningStrategyType",
            "HypothesisStatus",
            "ContradictionSeverity",
            "ContradictionResolutionStatus",
            "TraceStage",
            # Models
            "ReasoningRequest",
            "ReasoningResult",
            "ReasoningDecision",
            "ReasoningSession",
            "ReasoningContext",
            "ReasoningMetadata",
            "ReasoningConfidence",
            "ReasoningExplainabilityMetadata",
            "ReasoningHealth",
            "ReasoningMetrics",
            "ReasoningTrace",
            "ReasoningPath",
            "ReasoningStep",
            "Hypothesis",
            "HypothesisSet",
            "Inference",
            "InferenceChain",
            "Contradiction",
            "ReasoningStrategyConfig",
            # Events
            "ReasoningEvent",
            "ReasoningStarted",
            "HypothesisGenerated",
            "InferenceCompleted",
            "ContradictionDetected",
            "ReasoningCompleted",
            # Exceptions
            "ReasoningException",
            "HypothesisException",
            "InferenceException",
            "ContradictionException",
            # DTOs
            "ReasoningRequestDTO",
            "ReasoningResponseDTO",
            "ReasoningDecisionDTO",
            # Interfaces
            "ReasoningService",
            "ReasoningManager",
            "ReasoningCoordinator",
            "ReasoningStrategy",
            "HypothesisGenerator",
            "InferenceEngine",
            "ContradictionDetector",
            "ReasoningValidator",
            "ReasoningPathBuilder",
        }
        actual = set(reasoning.__all__)
        assert actual == expected, f"Missing: {expected - actual}, Extra: {actual - expected}"
