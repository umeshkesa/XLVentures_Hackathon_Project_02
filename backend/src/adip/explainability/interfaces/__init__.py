# INTERFACES FROZEN — Phase 1

"""Abstract interfaces for the Explainability Engine.

Defines all abstract interfaces used across explanation operations
following the Dependency Inversion Principle. All interfaces
are frozen after Phase 1.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from adip.explainability.contracts.models import (
    ExplanationCitation,
    ExplanationHealth,
    ExplanationMetrics,
    ExplanationNarrative,
    ExplanationRequest,
    ExplanationResult,
    ExplanationTrace,
)
from adip.explainability.dtos import (
    ExplanationPackageDTO,
    ExplanationRequestDTO,
    ExplanationResponseDTO,
)
from adip.explainability.enums import ExplanationLayer, NarrativeType


class ExplainabilityService(ABC):
    """Service-layer interface for the Explainability Engine.

    This is the ONLY public API for external consumers.
    All explanation operations MUST go through this interface.
    """

    @abstractmethod
    def explain(
        self,
        request: ExplanationRequestDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ExplanationResponseDTO | None:
        """Execute an explanation operation.

        Args:
            request: The explanation request DTO.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExplanationResponseDTO if authorized, None otherwise.
        """
        ...

    @abstractmethod
    def get_result(
        self,
        result_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ExplanationResult | None:
        """Retrieve an explanation result by ID.

        Args:
            result_id: The result identifier.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExplanationResult if found and authorized, None otherwise.
        """
        ...

    @abstractmethod
    def get_package(
        self,
        package_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ExplanationPackageDTO | None:
        """Retrieve an explanation package by ID.

        Args:
            package_id: The package identifier.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExplanationPackageDTO if found and authorized, None otherwise.
        """
        ...

    @abstractmethod
    def get_health(
        self,
        correlation_id: str = "",
    ) -> ExplanationHealth:
        """Get the health status of the Explainability Engine.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExplanationHealth with current component statuses.
        """
        ...

    @abstractmethod
    def get_metrics(
        self,
        correlation_id: str = "",
    ) -> ExplanationMetrics:
        """Get aggregated metrics for the Explainability Engine.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExplanationMetrics with current metric values.
        """
        ...


class ExplainabilityManager(ABC):
    """Internal manager interface for the Explainability Engine.

    Lightweight facade over the ExplainabilityCoordinator for
    internal use by ExplainabilityService. Not intended for
    external consumers.
    """

    @abstractmethod
    def execute_explanation(
        self,
        request: ExplanationRequest,
        correlation_id: str = "",
    ) -> ExplanationResult:
        """Execute an explanation operation.

        Args:
            request: The explanation request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The explanation result.
        """
        ...

    @abstractmethod
    def get_result(
        self,
        result_id: str,
    ) -> ExplanationResult | None:
        """Retrieve an explanation result by ID.

        Args:
            result_id: The result identifier.

        Returns:
            ExplanationResult if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_health(self) -> ExplanationHealth:
        """Get the health status of the Explainability Engine.

        Returns:
            ExplanationHealth with current component statuses.
        """
        ...

    @abstractmethod
    def get_metrics(self) -> ExplanationMetrics:
        """Get aggregated metrics for the Explainability Engine.

        Returns:
            ExplanationMetrics with current metric values.
        """
        ...


class ExplainabilityCoordinator(ABC):
    """Coordinator interface for the explanation pipeline.

    Orchestrates the full explanation pipeline by delegating
    to sub-components in the correct order.
    """

    @abstractmethod
    def explain(
        self,
        request: ExplanationRequest,
        correlation_id: str = "",
    ) -> ExplanationResult:
        """Execute a full explanation pipeline.

        Args:
            request: The explanation request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The explanation result.
        """
        ...

    @abstractmethod
    def get_result(
        self,
        result_id: str,
    ) -> ExplanationResult | None:
        """Retrieve an explanation result by ID.

        Args:
            result_id: The result identifier.

        Returns:
            ExplanationResult if found, None otherwise.
        """
        ...

    @abstractmethod
    def health(self) -> ExplanationHealth:
        """Get the health status of all sub-components.

        Returns:
            ExplanationHealth with component statuses.
        """
        ...

    @abstractmethod
    def metrics(self) -> ExplanationMetrics:
        """Get aggregated metrics from all sub-components.

        Returns:
            ExplanationMetrics with current values.
        """
        ...


class NarrativeBuilder(ABC):
    """Interface for narrative building.

    Builds explanation narratives tailored to specific audience
    layers from reasoning, evidence, and recommendation results.
    """

    @abstractmethod
    def build_narrative(
        self,
        request: ExplanationRequest,
        audience: ExplanationLayer,
        narrative_type: NarrativeType,
        correlation_id: str = "",
    ) -> ExplanationNarrative:
        """Build a single narrative for a specific audience.

        Args:
            request: The explanation request.
            audience: The target audience layer.
            narrative_type: The type of narrative to build.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The built explanation narrative.
        """
        ...

    @abstractmethod
    def build_narratives(
        self,
        request: ExplanationRequest,
        audiences: list[ExplanationLayer],
        correlation_id: str = "",
    ) -> list[ExplanationNarrative]:
        """Build narratives for multiple audiences.

        Args:
            request: The explanation request.
            audiences: The target audience layers.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of built explanation narratives.
        """
        ...


class CitationBuilder(ABC):
    """Interface for citation building.

    Builds citations linking explanation narratives to their
    source evidence, reasoning steps, and recommendations.
    """

    @abstractmethod
    def build_citations(
        self,
        narrative_id: str,
        reasoning_result_id: str,
        evidence_result_id: str,
        recommendation_result_id: str,
        correlation_id: str = "",
    ) -> list[ExplanationCitation]:
        """Build citations for a narrative from source results.

        Args:
            narrative_id: The narrative identifier.
            reasoning_result_id: The reasoning result ID.
            evidence_result_id: The evidence result ID.
            recommendation_result_id: The recommendation result ID.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of built explanation citations.
        """
        ...


class TraceBuilder(ABC):
    """Interface for trace recording.

    Records trace information for each stage of the
    explanation pipeline for observability.
    """

    @abstractmethod
    def record_stage(
        self,
        stage_name: str,
        operation: str,
        explanation_id: str,
        correlation_id: str = "",
        duration_ms: float = 0.0,
        success: bool = True,
        warnings: list[str] | None = None,
        errors: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExplanationTrace:
        """Record a trace for a pipeline stage.

        Args:
            stage_name: Name of the pipeline stage.
            operation: Operation being traced.
            explanation_id: The explanation identifier.
            correlation_id: Optional correlation ID for tracing.
            duration_ms: Duration of the stage in milliseconds.
            success: Whether the stage completed successfully.
            warnings: Warnings generated during this stage.
            errors: Errors generated during this stage.
            metadata: Additional trace metadata.

        Returns:
            The recorded explanation trace.
        """
        ...


class AudienceFormatter(ABC):
    """Interface for audience formatting.

    Formats explanation narratives for specific audience layers
    with appropriate detail levels and technical depth.
    """

    @abstractmethod
    def format(
        self,
        narrative: ExplanationNarrative,
        audience: ExplanationLayer,
        correlation_id: str = "",
    ) -> ExplanationNarrative:
        """Format a narrative for a specific audience.

        Args:
            narrative: The narrative to format.
            audience: The target audience layer.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The formatted explanation narrative.
        """
        ...


class ExplanationValidator(ABC):
    """Interface for explanation validation.

    Validates explanation requests and results for correctness,
    completeness, and consistency.
    """

    @abstractmethod
    def validate_request(
        self,
        request: ExplanationRequest,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate an explanation request.

        Args:
            request: The explanation request to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...

    @abstractmethod
    def validate_result(
        self,
        result: ExplanationResult,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate an explanation result.

        Args:
            result: The explanation result to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...
