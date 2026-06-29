"""Abstract ports for each stage of the planner pipeline."""

from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from adip.core.planner.models import (
    CapabilityMatch,
    ExecutionPlan,
    PlanningContext,
    PlanningGoal,
    PlanningRequest,
    PlanningResult,
    PlanningTask,
    ValidationResult,
)


class GoalAnalyzer(ABC):
    """Convert a request into normalized goals."""

    @abstractmethod
    async def analyze(self, request: PlanningRequest) -> tuple[PlanningGoal, ...]:
        """Analyze the request without selecting implementations."""
        raise NotImplementedError


class ContextAnalyzer(ABC):
    """Normalize and enrich planning context."""

    @abstractmethod
    async def analyze(self, request: PlanningRequest) -> PlanningContext:
        """Return the context to use for subsequent stages."""
        raise NotImplementedError


class CapabilityMatcher(ABC):
    """Match goals to advertised capability metadata."""

    @abstractmethod
    async def match(
        self,
        goals: tuple[PlanningGoal, ...],
        context: PlanningContext,
    ) -> tuple[CapabilityMatch, ...]:
        """Return candidate capability matches."""
        raise NotImplementedError


class TaskDecomposer(ABC):
    """Describe capability-backed tasks for analyzed goals."""

    @abstractmethod
    async def decompose(
        self,
        goals: tuple[PlanningGoal, ...],
        matches: tuple[CapabilityMatch, ...],
        context: PlanningContext,
    ) -> tuple[PlanningTask, ...]:
        """Return task contracts without executing them."""
        raise NotImplementedError


class PlanGenerator(ABC):
    """Construct a candidate execution plan from typed artifacts."""

    @abstractmethod
    async def generate(
        self,
        request: PlanningRequest,
        goal: PlanningGoal,
        tasks: tuple[PlanningTask, ...],
    ) -> ExecutionPlan:
        """Generate an execution plan contract."""
        raise NotImplementedError


class PlanValidator(ABC):
    """Validate a candidate execution plan."""

    @abstractmethod
    async def validate(
        self,
        plan: ExecutionPlan,
        context: PlanningContext,
    ) -> ValidationResult:
        """Return validation findings without mutating the plan."""
        raise NotImplementedError


class PlanOptimizer(ABC):
    """Produce an optional improved version of a valid plan."""

    @abstractmethod
    async def optimize(
        self,
        plan: ExecutionPlan,
        context: PlanningContext,
    ) -> ExecutionPlan:
        """Return the selected plan version."""
        raise NotImplementedError


class Replanner(ABC):
    """Create a replacement plan after a changed condition."""

    @abstractmethod
    async def replan(
        self,
        plan: ExecutionPlan,
        context: PlanningContext,
        reason: str,
    ) -> ExecutionPlan:
        """Return a new immutable plan version."""
        raise NotImplementedError


class ExecutionDispatcher(ABC):
    """Port through which an approved plan may later be dispatched."""

    @abstractmethod
    async def dispatch(self, plan: ExecutionPlan) -> uuid.UUID:
        """Return an external execution identifier."""
        raise NotImplementedError


class PlannerInterface(ABC):
    """Public application boundary for a future planner implementation."""

    @abstractmethod
    async def plan(self, request: PlanningRequest) -> PlanningResult:
        """Produce a typed planning result."""
        raise NotImplementedError
