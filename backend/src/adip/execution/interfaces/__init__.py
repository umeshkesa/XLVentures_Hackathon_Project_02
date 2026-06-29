# INTERFACES FROZEN — Phase 1
# Do not add, remove, or modify abstract methods.
# Do not add, remove, or modify interface classes.
# Any change requires full ADIP RFC process approval.

"""Abstract interfaces for the Action Engine.

Defines all abstract interfaces used across execution operations
following the Dependency Inversion Principle. All interfaces
are frozen after Phase 1.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from adip.execution.contracts.models import (
    ExecutionContext,
    ExecutionHealth,
    ExecutionMetrics,
    ExecutionPackage,
    ExecutionRequest,
    ExecutionResult,
    ExecutionSandbox,
    ExecutionSchedule,
    ExecutionSession,
    ExecutionTask,
    RetryPolicy,
)
from adip.execution.dtos import ExecutionRequestDTO, ExecutionResponseDTO
from adip.execution.enums import ExecutionState


class ExecutionService(ABC):
    """Service-layer interface for the Action Engine.

    This is the ONLY public API for external consumers.
    All execution operations MUST go through this interface.
    """

    @abstractmethod
    def start_execution(
        self,
        request: ExecutionRequestDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ExecutionResponseDTO | None:
        """Submit an execution request.

        Args:
            request: The execution request DTO.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExecutionResponseDTO if authorized, None otherwise.
        """
        ...

    @abstractmethod
    def get_session(
        self,
        session_id: str,
        correlation_id: str = "",
    ) -> ExecutionSession | None:
        """Retrieve an execution session by ID.

        Args:
            session_id: The session identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExecutionSession if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_result(
        self,
        result_id: str,
        correlation_id: str = "",
    ) -> ExecutionResult | None:
        """Retrieve an execution result by ID.

        Args:
            result_id: The result identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExecutionResult if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_package(
        self,
        package_id: str,
        correlation_id: str = "",
    ) -> ExecutionPackage | None:
        """Retrieve an execution package by ID.

        Args:
            package_id: The package identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExecutionPackage if found, None otherwise.
        """
        ...

    @abstractmethod
    def cancel_execution(
        self,
        session_id: str,
        reason: str = "",
        user_id: str = "",
        correlation_id: str = "",
    ) -> bool:
        """Cancel an active execution.

        Args:
            session_id: The session to cancel.
            reason: Optional reason for cancellation.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if cancelled successfully, False otherwise.
        """
        ...

    @abstractmethod
    def get_health(
        self,
        correlation_id: str = "",
    ) -> ExecutionHealth:
        """Get the health status of the Action Engine.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExecutionHealth with current component statuses.
        """
        ...

    @abstractmethod
    def get_metrics(
        self,
        correlation_id: str = "",
    ) -> ExecutionMetrics:
        """Get aggregated metrics for the Action Engine.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ExecutionMetrics with current metric values.
        """
        ...


class ExecutionManager(ABC):
    """Internal manager interface for the Action Engine.

    Lightweight facade over the ExecutionCoordinator for
    internal use by ExecutionService. Not intended for
    external consumers.
    """

    @abstractmethod
    def start_execution(
        self,
        request: ExecutionRequest,
        correlation_id: str = "",
    ) -> ExecutionSession:
        """Start an execution operation.

        Args:
            request: The execution request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created execution session.
        """
        ...

    @abstractmethod
    def get_session(
        self,
        session_id: str,
    ) -> ExecutionSession | None:
        """Retrieve an execution session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            ExecutionSession if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_result(
        self,
        result_id: str,
    ) -> ExecutionResult | None:
        """Retrieve an execution result by ID.

        Args:
            result_id: The result identifier.

        Returns:
            ExecutionResult if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_package(
        self,
        package_id: str,
    ) -> ExecutionPackage | None:
        """Retrieve an execution package by ID.

        Args:
            package_id: The package identifier.

        Returns:
            ExecutionPackage if found, None otherwise.
        """
        ...

    @abstractmethod
    def cancel_execution(
        self,
        session_id: str,
        reason: str = "",
    ) -> bool:
        """Cancel an active execution.

        Args:
            session_id: The session to cancel.
            reason: Optional reason for cancellation.

        Returns:
            True if cancelled successfully, False otherwise.
        """
        ...

    @abstractmethod
    def get_health(self) -> ExecutionHealth:
        """Get the health status of the Action Engine.

        Returns:
            ExecutionHealth with current component statuses.
        """
        ...

    @abstractmethod
    def get_metrics(self) -> ExecutionMetrics:
        """Get aggregated metrics for the Action Engine.

        Returns:
            ExecutionMetrics with current metric values.
        """
        ...


class ExecutionCoordinator(ABC):
    """Coordinator interface for the execution pipeline.

    Orchestrates the full execution pipeline by delegating
    to sub-components in the correct order.
    """

    @abstractmethod
    def execute(
        self,
        request: ExecutionRequest,
        correlation_id: str = "",
    ) -> ExecutionResult:
        """Execute a full execution pipeline.

        Args:
            request: The execution request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The execution result.
        """
        ...

    @abstractmethod
    def get_session(
        self,
        session_id: str,
    ) -> ExecutionSession | None:
        """Retrieve an execution session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            ExecutionSession if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_result(
        self,
        result_id: str,
    ) -> ExecutionResult | None:
        """Retrieve an execution result by ID.

        Args:
            result_id: The result identifier.

        Returns:
            ExecutionResult if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_package(
        self,
        package_id: str,
    ) -> ExecutionPackage | None:
        """Retrieve an execution package by ID.

        Args:
            package_id: The package identifier.

        Returns:
            ExecutionPackage if found, None otherwise.
        """
        ...

    @abstractmethod
    def cancel(
        self,
        session_id: str,
        reason: str = "",
    ) -> bool:
        """Cancel an active execution.

        Args:
            session_id: The session to cancel.
            reason: Optional reason for cancellation.

        Returns:
            True if cancelled successfully, False otherwise.
        """
        ...

    @abstractmethod
    def health(self) -> ExecutionHealth:
        """Get the health status of all sub-components.

        Returns:
            ExecutionHealth with component statuses.
        """
        ...

    @abstractmethod
    def metrics(self) -> ExecutionMetrics:
        """Get aggregated metrics from all sub-components.

        Returns:
            ExecutionMetrics with current values.
        """
        ...


class TaskExecutor(ABC):
    """Interface for task execution.

    Executes individual tasks within an execution package,
    handling the actual runtime invocation.
    """

    @abstractmethod
    def execute_task(
        self,
        task_id: str,
        package: ExecutionPackage,
        correlation_id: str = "",
    ) -> ExecutionResult:
        """Execute a single task.

        Args:
            task_id: The task identifier to execute.
            package: The execution package containing the task.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The execution result for this task.
        """
        ...

    @abstractmethod
    def validate_task(
        self,
        task_id: str,
        package: ExecutionPackage,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate a task before execution.

        Args:
            task_id: The task identifier to validate.
            package: The execution package containing the task.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...


class RetryManager(ABC):
    """Interface for retry management.

    Manages retry attempts for failed tasks according to
    the configured retry policy.
    """

    @abstractmethod
    def should_retry(
        self,
        task_id: str,
        attempt: int,
        error: str,
        policy: RetryPolicy,
        correlation_id: str = "",
    ) -> bool:
        """Determine if a task should be retried.

        Args:
            task_id: The task identifier.
            attempt: The current retry attempt number.
            error: The error that caused the failure.
            policy: The retry policy to evaluate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if the task should be retried, False otherwise.
        """
        ...

    @abstractmethod
    def get_delay(
        self,
        attempt: int,
        policy: RetryPolicy,
        correlation_id: str = "",
    ) -> int:
        """Calculate the delay before the next retry.

        Args:
            attempt: The current retry attempt number.
            policy: The retry policy to use for calculation.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Delay in seconds before the next retry.
        """
        ...


class CompensationManager(ABC):
    """Interface for compensation management.

    Manages compensation and rollback of executed tasks
    when execution fails or is cancelled.
    """

    @abstractmethod
    def execute_compensation(
        self,
        session_id: str,
        package: ExecutionPackage,
        correlation_id: str = "",
    ) -> bool:
        """Execute the compensation plan for a session.

        Args:
            session_id: The session to compensate for.
            package: The execution package with compensation plan.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if compensation succeeded, False otherwise.
        """
        ...

    @abstractmethod
    def validate_compensation(
        self,
        package: ExecutionPackage,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate that a compensation plan is sound.

        Args:
            package: The execution package to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...


class ExecutionMonitor(ABC):
    """Interface for execution monitoring.

    Monitors active executions, tracks progress, and
    reports state changes and anomalies.
    """

    @abstractmethod
    def get_session_state(
        self,
        session_id: str,
        correlation_id: str = "",
    ) -> ExecutionState:
        """Get the current state of an execution session.

        Args:
            session_id: The session identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The current ExecutionState.
        """
        ...

    @abstractmethod
    def get_active_sessions(
        self,
        correlation_id: str = "",
    ) -> list[ExecutionSession]:
        """Get all currently active execution sessions.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of active ExecutionSession objects.
        """
        ...


class ExecutionScheduler(ABC):
    """Interface for execution scheduling.

    Schedules execution packages for future or delayed
    execution based on the configured schedule.
    """

    @abstractmethod
    def schedule_execution(
        self,
        request: ExecutionRequest,
        schedule: ExecutionSchedule,
        correlation_id: str = "",
    ) -> str:
        """Schedule an execution for future delivery.

        Args:
            request: The execution request to schedule.
            schedule: The schedule defining when to execute.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The scheduled execution identifier.
        """
        ...

    @abstractmethod
    def cancel_scheduled(
        self,
        scheduled_id: str,
        correlation_id: str = "",
    ) -> bool:
        """Cancel a previously scheduled execution.

        Args:
            scheduled_id: The scheduled execution identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            True if cancelled successfully, False otherwise.
        """
        ...


class SandboxExecutor(ABC):
    """Interface for sandboxed execution.

    Executes tasks within a sandboxed environment with
    resource limits and isolation boundaries.
    """

    @abstractmethod
    def execute_in_sandbox(
        self,
        task: ExecutionTask,
        sandbox: ExecutionSandbox,
        correlation_id: str = "",
    ) -> ExecutionResult:
        """Execute a task within a sandboxed environment.

        Args:
            task: The task to execute.
            sandbox: The sandbox configuration.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The execution result.
        """
        ...

    @abstractmethod
    def validate_sandbox(
        self,
        sandbox: ExecutionSandbox,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate that a sandbox configuration is correct.

        Args:
            sandbox: The sandbox configuration to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...


class ExecutionAdapter(ABC):
    """Interface for external system adapters.

    Defines the contract for adapters that connect the
    execution engine to external systems, services, or
    devices.
    """

    @abstractmethod
    def execute(
        self,
        task: ExecutionTask,
        configuration: dict[str, Any],
        correlation_id: str = "",
    ) -> ExecutionResult:
        """Execute a task through this adapter.

        Args:
            task: The task to execute via this adapter.
            configuration: Adapter-specific configuration.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The execution result.
        """
        ...

    @abstractmethod
    def validate(
        self,
        configuration: dict[str, Any],
        correlation_id: str = "",
    ) -> list[str]:
        """Validate the adapter configuration.

        Args:
            configuration: The adapter configuration to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...

    @abstractmethod
    def get_capabilities(
        self,
        correlation_id: str = "",
    ) -> list[str]:
        """Get the capabilities supported by this adapter.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of capability names.
        """
        ...
