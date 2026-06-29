"""Planner-specific exception taxonomy for future implementations."""

from adip.core.exceptions.base import PlannerException


class PlannerContractException(PlannerException):
    """Base for failures within planner contract implementations."""


class GoalAnalysisException(PlannerContractException):
    """Raised when goal analysis cannot produce a usable goal."""

    code = "planner_goal_analysis_error"


class ContextAnalysisException(PlannerContractException):
    """Raised when planning context cannot be normalized."""

    code = "planner_context_analysis_error"


class CapabilityMatchingException(PlannerContractException):
    """Raised when required capabilities cannot be matched."""

    code = "planner_capability_matching_error"


class TaskDecompositionException(PlannerContractException):
    """Raised when goals cannot be represented as tasks."""

    code = "planner_task_decomposition_error"


class PlanGenerationException(PlannerContractException):
    """Raised when a candidate execution plan cannot be produced."""

    code = "planner_generation_error"


class PlanValidationException(PlannerContractException):
    """Raised when plan validation cannot be completed."""

    code = "planner_validation_error"


class PlanOptimizationException(PlannerContractException):
    """Raised when plan optimization fails."""

    code = "planner_optimization_error"


class ReplanningException(PlannerContractException):
    """Raised when a replacement plan cannot be produced."""

    code = "planner_replanning_error"


class ExecutionDispatchException(PlannerContractException):
    """Raised when a plan cannot be handed to an execution adapter."""

    code = "planner_dispatch_error"
