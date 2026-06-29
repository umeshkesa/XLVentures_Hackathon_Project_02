# INTERFACES FROZEN — Phase 3.5
# Do not add, remove, or modify abstract methods.
# Do not add, remove, or modify interface classes.
# Any change requires full ADIP RFC process approval.

"""Abstract interfaces for the Reasoning Engine.

Defines all abstract interfaces used across reasoning operations
following the Dependency Inversion Principle. All interfaces
are frozen after Phase 3.5.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from adip.reasoning.contracts.models import (
    Contradiction,
    Hypothesis,
    HypothesisSet,
    Inference,
    InferenceChain,
    ReasoningConfidence,
    ReasoningContext,
    ReasoningDecision,
    ReasoningHealth,
    ReasoningMetrics,
    ReasoningPath,
    ReasoningRequest,
    ReasoningResult,
    ReasoningSession,
)
from adip.reasoning.dtos import ReasoningDecisionDTO, ReasoningRequestDTO, ReasoningResponseDTO


class ReasoningService(ABC):
    """Service-layer interface for the Reasoning Engine.

    This is the ONLY public API for external consumers.
    All reasoning operations MUST go through this interface.
    """

    @abstractmethod
    def reason(
        self,
        request: ReasoningRequestDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ReasoningResponseDTO | None:
        """Execute a reasoning operation.

        Args:
            request: The reasoning request DTO.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReasoningResponseDTO if authorized, None otherwise.
        """
        ...

    @abstractmethod
    def get_result(
        self,
        result_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ReasoningResult | None:
        """Retrieve a reasoning result by ID.

        Args:
            result_id: The result identifier.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReasoningResult if found and authorized, None otherwise.
        """
        ...

    @abstractmethod
    def get_health(
        self,
        correlation_id: str = "",
    ) -> ReasoningHealth:
        """Get the health status of the Reasoning Engine.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReasoningHealth with current component statuses.
        """
        ...

    @abstractmethod
    def get_metrics(
        self,
        correlation_id: str = "",
    ) -> ReasoningMetrics:
        """Get aggregated metrics for the Reasoning Engine.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ReasoningMetrics with current metric values.
        """
        ...


class ReasoningManager(ABC):
    """Internal manager interface for the Reasoning Engine.

    Lightweight facade over the ReasoningCoordinator for
    internal use by ReasoningService. Not intended for
    external consumers.
    """

    @abstractmethod
    def execute_reasoning(
        self,
        request: ReasoningRequest,
        correlation_id: str = "",
    ) -> ReasoningResult:
        """Execute a reasoning operation.

        Args:
            request: The reasoning request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The reasoning result.
        """
        ...

    @abstractmethod
    def get_result(
        self,
        result_id: str,
    ) -> ReasoningResult | None:
        """Retrieve a reasoning result by ID.

        Args:
            result_id: The result identifier.

        Returns:
            ReasoningResult if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_health(self) -> ReasoningHealth:
        """Get the health status of the Reasoning Engine.

        Returns:
            ReasoningHealth with current component statuses.
        """
        ...

    @abstractmethod
    def get_metrics(self) -> ReasoningMetrics:
        """Get aggregated metrics for the Reasoning Engine.

        Returns:
            ReasoningMetrics with current metric values.
        """
        ...


class ReasoningCoordinator(ABC):
    """Coordinator interface for the reasoning pipeline.

    Orchestrates the full reasoning pipeline by delegating
    to sub-components in the correct order.
    """

    @abstractmethod
    def reason(
        self,
        request: ReasoningRequest,
        correlation_id: str = "",
    ) -> ReasoningResult:
        """Execute a full reasoning pipeline.

        Args:
            request: The reasoning request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The reasoning result.
        """
        ...

    @abstractmethod
    def get_result(
        self,
        result_id: str,
    ) -> ReasoningResult | None:
        """Retrieve a reasoning result by ID.

        Args:
            result_id: The result identifier.

        Returns:
            ReasoningResult if found, None otherwise.
        """
        ...

    @abstractmethod
    def health(self) -> ReasoningHealth:
        """Get the health status of all sub-components.

        Returns:
            ReasoningHealth with component statuses.
        """
        ...

    @abstractmethod
    def metrics(self) -> ReasoningMetrics:
        """Get aggregated metrics from all sub-components.

        Returns:
            ReasoningMetrics with current values.
        """
        ...


class ReasoningStrategy(ABC):
    """Strategy interface for reasoning approaches.

    Defines the contract for different reasoning strategies
    that can be plugged into the reasoning pipeline.
    """

    @abstractmethod
    def execute(
        self,
        context: ReasoningContext,
        hypotheses: list[Hypothesis] | None = None,
        correlation_id: str = "",
    ) -> ReasoningPath:
        """Execute this reasoning strategy.

        Args:
            context: The reasoning context.
            hypotheses: Optional existing hypotheses to reason about.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A reasoning path produced by this strategy.
        """
        ...

    @abstractmethod
    def get_strategy_type(self) -> str:
        """Get the type of this reasoning strategy.

        Returns:
            String identifier for the strategy type.
        """
        ...


class HypothesisGenerator(ABC):
    """Interface for hypothesis generation.

    Generates hypotheses from evidence packages and context
    for evaluation during reasoning.
    """

    @abstractmethod
    def generate(
        self,
        evidence_ids: list[str],
        context: ReasoningContext,
        count: int = 5,
        correlation_id: str = "",
    ) -> HypothesisSet:
        """Generate hypotheses from evidence.

        Args:
            evidence_ids: Evidence IDs to generate hypotheses from.
            context: The reasoning context.
            count: Maximum number of hypotheses to generate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            A set of generated hypotheses.
        """
        ...

    @abstractmethod
    def validate(
        self,
        hypothesis: Hypothesis,
        correlation_id: str = "",
    ) -> bool:
        """Validate a hypothesis for correctness.

        Args:
            hypothesis: The hypothesis to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if the hypothesis is valid, False otherwise.
        """
        ...


class InferenceEngine(ABC):
    """Interface for the inference engine.

    Draws logical inferences from hypotheses, evidence,
    and rules during reasoning.
    """

    @abstractmethod
    def infer(
        self,
        premise: str,
        hypothesis_id: str | None = None,
        correlation_id: str = "",
    ) -> Inference:
        """Draw an inference from a premise.

        Args:
            premise: The premise to infer from.
            hypothesis_id: Optional hypothesis ID for context.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The resulting inference.
        """
        ...

    @abstractmethod
    def chain(
        self,
        inferences: list[Inference],
        correlation_id: str = "",
    ) -> InferenceChain:
        """Chain multiple inferences into a logical sequence.

        Args:
            inferences: The inferences to chain together.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            An inference chain connecting the inferences.
        """
        ...


class ContradictionDetector(ABC):
    """Interface for contradiction detection.

    Detects contradictions between evidence, hypotheses,
    and inferences during reasoning.
    """

    @abstractmethod
    def detect(
        self,
        hypotheses: list[Hypothesis],
        correlation_id: str = "",
    ) -> list[Contradiction]:
        """Detect contradictions among hypotheses.

        Args:
            hypotheses: The hypotheses to check for contradictions.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of detected contradictions.
        """
        ...

    @abstractmethod
    def resolve(
        self,
        contradiction: Contradiction,
        resolution: str,
        correlation_id: str = "",
    ) -> Contradiction:
        """Resolve a contradiction.

        Args:
            contradiction: The contradiction to resolve.
            resolution: The resolution to apply.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The resolved contradiction.
        """
        ...


class ReasoningValidator(ABC):
    """Interface for reasoning validation.

    Validates reasoning inputs, intermediate states, and
    final results for correctness and consistency.
    """

    @abstractmethod
    def validate_request(
        self,
        request: ReasoningRequest,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate a reasoning request.

        Args:
            request: The reasoning request to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...

    @abstractmethod
    def validate_result(
        self,
        result: ReasoningResult,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate a reasoning result.

        Args:
            result: The reasoning result to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...


class ReasoningPathBuilder(ABC):
    """Interface for reasoning path construction.

    Builds and manages reasoning paths that trace the
    logical flow from evidence to conclusions.
    """

    @abstractmethod
    def build_path(
        self,
        steps: list[ReasoningStep],
        request_id: str,
        strategy: str = "HYBRID",
        correlation_id: str = "",
    ) -> ReasoningPath:
        """Build a reasoning path from steps.

        Args:
            steps: The reasoning steps to include.
            request_id: The request this path belongs to.
            strategy: The strategy used for this path.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The constructed reasoning path.
        """
        ...

    @abstractmethod
    def add_step(
        self,
        path: ReasoningPath,
        step: ReasoningStep,
        correlation_id: str = "",
    ) -> ReasoningPath:
        """Add a step to an existing reasoning path.

        Args:
            path: The reasoning path to extend.
            step: The step to add.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The updated reasoning path.
        """
        ...
