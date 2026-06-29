"""Abstract interfaces for planner pipeline components."""

from __future__ import annotations

import abc
from typing import Protocol, runtime_checkable

from adip.planner.contracts.models import (
    CapabilityMatch,
    ExecutionPlan,
    PlanningContext,
    PlanningGoal,
    PlanningRequest,
    PlanningResult,
    PlanningTask,
    ValidationResult,
)
from adip.planner.enums import PlanningStrategyEnum


class GoalAnalyzer(abc.ABC):
    """Analyzes a planning goal, enriching it with metadata."""

    @abc.abstractmethod
    async def analyze(self, goal: PlanningGoal) -> PlanningGoal:
        """Analyze and enrich the planning goal.

        Returns an enriched *goal* (e.g. intent, domain, entities,
        ambiguity_score populated).
        """
        ...


class ContextAnalyzer(abc.ABC):
    """Gathers / enriches the planning context."""

    @abc.abstractmethod
    async def analyze(
        self, goal: PlanningGoal, context: PlanningContext
    ) -> PlanningContext:
        """Analyze and enrich the planning context.

        Returns the context with additional capabilities or knowledge
        derived from the goal and raw context.
        """
        ...


@runtime_checkable
class CapabilityMatcher(Protocol):
    """Matches available capabilities to task descriptions."""

    async def match_capabilities(
        self, task_description: str, context: PlanningContext
    ) -> list[CapabilityMatch]:
        ...


class TaskDecomposer(abc.ABC):
    """Breaks a goal into actionable tasks."""

    @abc.abstractmethod
    async def decompose(
        self, goal: PlanningGoal, context: PlanningContext
    ) -> list[PlanningTask]:
        ...


class PlanGenerator(abc.ABC):
    """Generates an ExecutionPlan from a list of tasks."""

    @abc.abstractmethod
    async def generate(
        self, tasks: list[PlanningTask], context: PlanningContext, goal: PlanningGoal
    ) -> ExecutionPlan:
        ...


class PlanValidator(abc.ABC):
    """Validates an execution plan."""

    @abc.abstractmethod
    async def validate(
        self, plan: ExecutionPlan, context: PlanningContext
    ) -> ValidationResult:
        ...


class PlanOptimizer(abc.ABC):
    """Optimises an execution plan."""

    @abc.abstractmethod
    async def optimize(
        self, plan: ExecutionPlan, context: PlanningContext, goal: PlanningGoal
    ) -> ExecutionPlan:
        ...


class Replanner(abc.ABC):
    """Replans when execution deviates."""

    @abc.abstractmethod
    async def replan(
        self,
        original_plan: ExecutionPlan,
        current_context: PlanningContext,
        deviation_reason: str,
        goal: PlanningGoal,
    ) -> ExecutionPlan | None:
        ...


class ExecutionDispatcher(abc.ABC):
    """Dispatches a single task for execution."""

    @abc.abstractmethod
    async def dispatch(
        self, task: PlanningTask, context: PlanningContext
    ) -> PlanningTask:
        ...


class ConfidenceCalculator(abc.ABC):
    """Calculates overall plan confidence as a 0-100 score."""

    @abc.abstractmethod
    async def calculate(
        self,
        plan: ExecutionPlan,
        validation: ValidationResult,
        context: PlanningContext,
        goal: PlanningGoal,
    ) -> float:
        """Return a confidence score from 0.0 (lowest) to 100.0 (highest)."""
        ...


class StrategySelector(abc.ABC):
    """Selects planning strategy from goal + context."""

    @abc.abstractmethod
    async def select(
        self, goal: PlanningGoal, context: PlanningContext
    ) -> PlanningStrategyEnum:
        ...


class PlannerInterface(abc.ABC):
    """Orchestrates the full planning pipeline."""

    @abc.abstractmethod
    async def plan(self, request: PlanningRequest) -> PlanningResult:
        ...
