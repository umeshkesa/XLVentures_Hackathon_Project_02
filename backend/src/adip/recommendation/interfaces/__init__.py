# INTERFACES FROZEN — Phase 3.5
# Do not add, remove, or modify abstract methods.
# Do not add, remove, or modify interface classes.
# Any change requires full ADIP RFC process approval.

"""Abstract interfaces for the Recommendation Engine.

Defines all abstract interfaces used across recommendation operations
following the Dependency Inversion Principle. All interfaces
are frozen after Phase 3.5.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from adip.recommendation.contracts.models import (
    RecommendationCandidate,
    RecommendationConfidence,
    RecommendationContext,
    RecommendationDecision,
    RecommendationHealth,
    RecommendationMetrics,
    RecommendationPackage,
    RecommendationRequest,
    RecommendationResult,
    RecommendationSession,
)
from adip.recommendation.dtos import (
    RecommendationPackageDTO,
    RecommendationRequestDTO,
    RecommendationResponseDTO,
)


class RecommendationService(ABC):
    """Service-layer interface for the Recommendation Engine.

    This is the ONLY public API for external consumers.
    All recommendation operations MUST go through this interface.
    """

    @abstractmethod
    def recommend(
        self,
        request: RecommendationRequestDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> RecommendationResponseDTO | None:
        """Execute a recommendation operation.

        Args:
            request: The recommendation request DTO.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            RecommendationResponseDTO if authorized, None otherwise.
        """
        ...

    @abstractmethod
    def get_result(
        self,
        result_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> RecommendationResult | None:
        """Retrieve a recommendation result by ID.

        Args:
            result_id: The result identifier.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            RecommendationResult if found and authorized, None otherwise.
        """
        ...

    @abstractmethod
    def get_package(
        self,
        package_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> RecommendationPackageDTO | None:
        """Retrieve a recommendation package by ID.

        Args:
            package_id: The package identifier.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            RecommendationPackageDTO if found and authorized, None otherwise.
        """
        ...

    @abstractmethod
    def get_health(
        self,
        correlation_id: str = "",
    ) -> RecommendationHealth:
        """Get the health status of the Recommendation Engine.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            RecommendationHealth with current component statuses.
        """
        ...

    @abstractmethod
    def get_metrics(
        self,
        correlation_id: str = "",
    ) -> RecommendationMetrics:
        """Get aggregated metrics for the Recommendation Engine.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            RecommendationMetrics with current metric values.
        """
        ...


class RecommendationManager(ABC):
    """Internal manager interface for the Recommendation Engine.

    Lightweight facade over the RecommendationCoordinator for
    internal use by RecommendationService. Not intended for
    external consumers.
    """

    @abstractmethod
    def execute_recommendation(
        self,
        request: RecommendationRequest,
        correlation_id: str = "",
    ) -> RecommendationResult:
        """Execute a recommendation operation.

        Args:
            request: The recommendation request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The recommendation result.
        """
        ...

    @abstractmethod
    def get_result(
        self,
        result_id: str,
    ) -> RecommendationResult | None:
        """Retrieve a recommendation result by ID.

        Args:
            result_id: The result identifier.

        Returns:
            RecommendationResult if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_health(self) -> RecommendationHealth:
        """Get the health status of the Recommendation Engine.

        Returns:
            RecommendationHealth with current component statuses.
        """
        ...

    @abstractmethod
    def get_metrics(self) -> RecommendationMetrics:
        """Get aggregated metrics for the Recommendation Engine.

        Returns:
            RecommendationMetrics with current metric values.
        """
        ...


class RecommendationCoordinator(ABC):
    """Coordinator interface for the recommendation pipeline.

    Orchestrates the full recommendation pipeline by delegating
    to sub-components in the correct order.
    """

    @abstractmethod
    def recommend(
        self,
        request: RecommendationRequest,
        correlation_id: str = "",
    ) -> RecommendationResult:
        """Execute a full recommendation pipeline.

        Args:
            request: The recommendation request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The recommendation result.
        """
        ...

    @abstractmethod
    def get_result(
        self,
        result_id: str,
    ) -> RecommendationResult | None:
        """Retrieve a recommendation result by ID.

        Args:
            result_id: The result identifier.

        Returns:
            RecommendationResult if found, None otherwise.
        """
        ...

    @abstractmethod
    def health(self) -> RecommendationHealth:
        """Get the health status of all sub-components.

        Returns:
            RecommendationHealth with component statuses.
        """
        ...

    @abstractmethod
    def metrics(self) -> RecommendationMetrics:
        """Get aggregated metrics from all sub-components.

        Returns:
            RecommendationMetrics with current values.
        """
        ...


class RecommendationGenerator(ABC):
    """Interface for recommendation generation.

    Generates recommendation candidates from reasoning results
    and context for downstream ranking and validation.
    """

    @abstractmethod
    def generate(
        self,
        reasoning_result_id: str,
        context: RecommendationContext,
        count: int = 5,
        correlation_id: str = "",
    ) -> list[RecommendationCandidate]:
        """Generate recommendation candidates from a reasoning result.

        Args:
            reasoning_result_id: The reasoning result to transform.
            context: The recommendation context.
            count: Maximum number of candidates to generate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of generated recommendation candidates.
        """
        ...

    @abstractmethod
    def validate(
        self,
        candidate: RecommendationCandidate,
        correlation_id: str = "",
    ) -> bool:
        """Validate a recommendation candidate for correctness.

        Args:
            candidate: The candidate to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if the candidate is valid, False otherwise.
        """
        ...


class RecommendationRanker(ABC):
    """Interface for recommendation ranking.

    Ranks and prioritizes recommendation candidates based on
    scores, benefits, risks, and constraints.
    """

    @abstractmethod
    def rank(
        self,
        candidates: list[RecommendationCandidate],
        correlation_id: str = "",
    ) -> list[RecommendationCandidate]:
        """Rank recommendation candidates by priority.

        Args:
            candidates: The candidates to rank.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Ranked list of candidates (highest priority first).
        """
        ...

    @abstractmethod
    def select_best(
        self,
        candidates: list[RecommendationCandidate],
        correlation_id: str = "",
    ) -> RecommendationCandidate | None:
        """Select the best candidate from a ranked list.

        Args:
            candidates: The ranked candidates.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The best candidate, or None if the list is empty.
        """
        ...


class RecommendationValidator(ABC):
    """Interface for recommendation validation.

    Validates recommendation inputs, intermediate states, and
    final results for correctness and consistency.
    """

    @abstractmethod
    def validate_request(
        self,
        request: RecommendationRequest,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate a recommendation request.

        Args:
            request: The recommendation request to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...

    @abstractmethod
    def validate_result(
        self,
        result: RecommendationResult,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate a recommendation result.

        Args:
            result: The recommendation result to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...


class RecommendationPolicyEngine(ABC):
    """Interface for the recommendation policy engine.

    Evaluates policies and constraints against recommendation
    requests, candidates, and packages.
    """

    @abstractmethod
    def check_policy(
        self,
        request: RecommendationRequest,
        correlation_id: str = "",
    ) -> list[str]:
        """Check policy compliance for a recommendation request.

        Args:
            request: The recommendation request to check.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of policy violations (empty if compliant).
        """
        ...

    @abstractmethod
    def check_candidate(
        self,
        candidate: RecommendationCandidate,
        correlation_id: str = "",
    ) -> list[str]:
        """Check policy compliance for a recommendation candidate.

        Args:
            candidate: The candidate to check.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of policy violations (empty if compliant).
        """
        ...


class ImpactEstimator(ABC):
    """Interface for impact estimation.

    Estimates the impact of a recommendation candidate across
    multiple dimensions including cost, time, safety, and quality.
    """

    @abstractmethod
    def estimate(
        self,
        candidate: RecommendationCandidate,
        correlation_id: str = "",
    ) -> dict[str, float]:
        """Estimate the impact of a recommendation candidate.

        Args:
            candidate: The candidate to estimate impact for.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Dictionary of impact dimensions to estimated values.
        """
        ...


class BenefitAnalyzer(ABC):
    """Interface for benefit analysis.

    Analyzes and estimates the expected benefits of a
    recommendation candidate.
    """

    @abstractmethod
    def analyze(
        self,
        candidate: RecommendationCandidate,
        correlation_id: str = "",
    ) -> list[dict[str, Any]]:
        """Analyze the benefits of a recommendation candidate.

        Args:
            candidate: The candidate to analyze benefits for.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of benefit analysis dictionaries.
        """
        ...
