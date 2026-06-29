# INTERFACES FROZEN — Phase 1
# Do not add, remove, or modify abstract methods.
# Do not add, remove, or modify interface classes.
# Any change requires full ADIP RFC process approval.

"""Abstract interfaces for the Action Manager.

Defines all abstract interfaces used across action operations
following the Dependency Inversion Principle. All interfaces
are frozen after Phase 1.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from adip.actions.contracts.models import (
    ActionDecision,
    ActionHealth,
    ActionMetrics,
    ActionPlan,
    ActionRequest,
    ActionSession,
)
from adip.actions.dtos import ActionRequestDTO, ActionResponseDTO
from adip.actions.enums import ActionPriority, ActionType, ExecutionReadiness


class ActionService(ABC):
    """Service-layer interface for the Action Manager.

    This is the ONLY public API for external consumers.
    All action planning operations MUST go through this interface.
    """

    @abstractmethod
    def plan_action(
        self,
        request: ActionRequestDTO,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ActionResponseDTO | None:
        """Submit an action planning request.

        Args:
            request: The action request DTO.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ActionResponseDTO if authorized, None otherwise.
        """
        ...

    @abstractmethod
    def get_decision(
        self,
        decision_id: str,
        user_id: str = "",
        correlation_id: str = "",
    ) -> ActionDecision | None:
        """Retrieve an action decision by ID.

        Args:
            decision_id: The decision identifier.
            user_id: Optional user identifier for auth.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ActionDecision if found and authorized, None otherwise.
        """
        ...

    @abstractmethod
    def get_plan(
        self,
        plan_id: str,
        correlation_id: str = "",
    ) -> ActionPlan | None:
        """Retrieve an action plan by ID.

        Args:
            plan_id: The plan identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ActionPlan if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_session(
        self,
        session_id: str,
        correlation_id: str = "",
    ) -> ActionSession | None:
        """Retrieve an action session by ID.

        Args:
            session_id: The session identifier.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ActionSession if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_health(
        self,
        correlation_id: str = "",
    ) -> ActionHealth:
        """Get the health status of the Action Manager.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ActionHealth with current component statuses.
        """
        ...

    @abstractmethod
    def get_metrics(
        self,
        correlation_id: str = "",
    ) -> ActionMetrics:
        """Get aggregated metrics for the Action Manager.

        Args:
            correlation_id: Optional correlation ID for tracing.

        Returns:
            ActionMetrics with current metric values.
        """
        ...


class ActionManager(ABC):
    """Internal manager interface for the Action Manager.

    Lightweight facade over the ActionCoordinator for
    internal use by ActionService. Not intended for
    external consumers.
    """

    @abstractmethod
    def start_planning(
        self,
        request: ActionRequest,
        correlation_id: str = "",
    ) -> ActionSession:
        """Start an action planning operation.

        Args:
            request: The action request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The created action session.
        """
        ...

    @abstractmethod
    def get_decision(
        self,
        decision_id: str,
    ) -> ActionDecision | None:
        """Retrieve an action decision by ID.

        Args:
            decision_id: The decision identifier.

        Returns:
            ActionDecision if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_plan(
        self,
        plan_id: str,
    ) -> ActionPlan | None:
        """Retrieve an action plan by ID.

        Args:
            plan_id: The plan identifier.

        Returns:
            ActionPlan if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_session(
        self,
        session_id: str,
    ) -> ActionSession | None:
        """Retrieve an action session by ID.

        Args:
            session_id: The session identifier.

        Returns:
            ActionSession if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_health(self) -> ActionHealth:
        """Get the health status of the Action Manager.

        Returns:
            ActionHealth with current component statuses.
        """
        ...

    @abstractmethod
    def get_metrics(self) -> ActionMetrics:
        """Get aggregated metrics for the Action Manager.

        Returns:
            ActionMetrics with current metric values.
        """
        ...


class ActionCoordinator(ABC):
    """Coordinator interface for the action planning pipeline.

    Orchestrates the full action planning pipeline by
    delegating to sub-components in the correct order.
    """

    @abstractmethod
    def plan(
        self,
        request: ActionRequest,
        correlation_id: str = "",
    ) -> ActionDecision:
        """Execute a full action planning pipeline.

        Args:
            request: The action request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The action decision.
        """
        ...

    @abstractmethod
    def get_decision(
        self,
        decision_id: str,
    ) -> ActionDecision | None:
        """Retrieve an action decision by ID.

        Args:
            decision_id: The decision identifier.

        Returns:
            ActionDecision if found, None otherwise.
        """
        ...

    @abstractmethod
    def get_plan(
        self,
        plan_id: str,
    ) -> ActionPlan | None:
        """Retrieve an action plan by ID.

        Args:
            plan_id: The plan identifier.

        Returns:
            ActionPlan if found, None otherwise.
        """
        ...

    @abstractmethod
    def health(self) -> ActionHealth:
        """Get the health status of all sub-components.

        Returns:
            ActionHealth with component statuses.
        """
        ...

    @abstractmethod
    def metrics(self) -> ActionMetrics:
        """Get aggregated metrics from all sub-components.

        Returns:
            ActionMetrics with current values.
        """
        ...


class ActionPlanner(ABC):
    """Interface for action plan generation.

    Generates a structured ActionPlan from an ActionRequest,
    decomposing the approved action into ordered steps with
    dependencies, resources, and schedule.
    """

    @abstractmethod
    def generate_plan(
        self,
        request: ActionRequest,
        correlation_id: str = "",
    ) -> ActionPlan:
        """Generate an action plan from a request.

        Args:
            request: The action request.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The generated ActionPlan.
        """
        ...

    @abstractmethod
    def validate_plan(
        self,
        plan: ActionPlan,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate an action plan for correctness.

        Args:
            plan: The action plan to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...


class DependencyResolver(ABC):
    """Interface for dependency resolution.

    Discovers, resolves, and validates dependencies between
    action steps and external resources required for
    successful plan execution.
    """

    @abstractmethod
    def resolve_dependencies(
        self,
        plan: ActionPlan,
        correlation_id: str = "",
    ) -> list[ActionPlan]:
        """Resolve dependencies for an action plan.

        Args:
            plan: The action plan to resolve dependencies for.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Ordered list of plans in dependency order.
        """
        ...

    @abstractmethod
    def validate_dependencies(
        self,
        plan: ActionPlan,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate dependencies for an action plan.

        Args:
            plan: The action plan to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...


class ResourceAllocator(ABC):
    """Interface for resource allocation.

    Allocates personnel, equipment, and materials required
    for executing an action plan.
    """

    @abstractmethod
    def allocate_resources(
        self,
        plan: ActionPlan,
        correlation_id: str = "",
    ) -> ActionPlan:
        """Allocate resources for an action plan.

        Args:
            plan: The action plan to allocate resources for.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The updated ActionPlan with resource allocations.
        """
        ...

    @abstractmethod
    def validate_resources(
        self,
        plan: ActionPlan,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate resource allocations for an action plan.

        Args:
            plan: The action plan to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...


class SchedulePlanner(ABC):
    """Interface for schedule planning.

    Creates and validates execution schedules for action
    plans based on dependencies, resource availability,
    and timing constraints.
    """

    @abstractmethod
    def create_schedule(
        self,
        plan: ActionPlan,
        correlation_id: str = "",
    ) -> ActionPlan:
        """Create an execution schedule for an action plan.

        Args:
            plan: The action plan to schedule.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The updated ActionPlan with schedule.
        """
        ...

    @abstractmethod
    def validate_schedule(
        self,
        plan: ActionPlan,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate the schedule of an action plan.

        Args:
            plan: The action plan to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...


class RollbackPlanner(ABC):
    """Interface for rollback planning.

    Generates rollback plans that safely revert action
    execution in case of failure or cancellation.
    """

    @abstractmethod
    def create_rollback(
        self,
        plan: ActionPlan,
        correlation_id: str = "",
    ) -> RollbackPlan | None:
        """Create a rollback plan for an action plan.

        Args:
            plan: The action plan to create rollback for.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            The RollbackPlan if rollback is needed, None otherwise.
        """
        ...

    @abstractmethod
    def validate_rollback(
        self,
        rollback: RollbackPlan,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate a rollback plan.

        Args:
            rollback: The rollback plan to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if valid).
        """
        ...


class ReadinessValidator(ABC):
    """Interface for execution readiness validation.

    Assesses whether an action plan is ready for execution
    by validating all dependencies, resources, schedule,
    and preconditions are satisfied.
    """

    @abstractmethod
    def check_readiness(
        self,
        plan: ActionPlan,
        correlation_id: str = "",
    ) -> tuple[ExecutionReadiness, str]:
        """Check execution readiness for an action plan.

        Args:
            plan: The action plan to check.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            Tuple of (ExecutionReadiness status, reason string).
        """
        ...

    @abstractmethod
    def validate_readiness(
        self,
        plan: ActionPlan,
        correlation_id: str = "",
    ) -> list[str]:
        """Validate execution readiness conditions.

        Args:
            plan: The action plan to validate.
            correlation_id: Optional correlation ID for tracing.

        Returns:
            List of validation violations (empty if ready).
        """
        ...
