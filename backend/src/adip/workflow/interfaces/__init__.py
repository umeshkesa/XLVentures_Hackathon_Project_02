"""Abstract interfaces for Workflow Engine components.

All interfaces follow dependency inversion — consumers depend on
abstractions, not concrete implementations.

This module defines the frozen public contract for all ADIP modules
that integrate with the Workflow Engine (Managers, Engines, Plugins,
Action Engine, Decision Review Layer, etc.).
"""

from __future__ import annotations

import abc
from typing import Protocol, runtime_checkable

from adip.workflow.contracts.models import (
    TaskResult,
    WorkflowDecision,
    WorkflowGraph,
    WorkflowRequest,
    WorkflowResult,
    WorkflowTask,
)


class GraphBuilder(abc.ABC):
    """Builds a ``WorkflowGraph`` from a ``WorkflowRequest``."""

    @abc.abstractmethod
    async def build(self, request: WorkflowRequest) -> WorkflowGraph:
        """Construct the execution graph from the request."""
        ...


class TaskScheduler(abc.ABC):
    """Decides which task to execute next based on graph state."""

    @abc.abstractmethod
    async def schedule(self, graph: WorkflowGraph) -> list[WorkflowTask]:
        """Return the next set of tasks eligible for execution."""
        ...


class TaskDispatcher(abc.ABC):
    """Dispatches a task to an executor."""

    @abc.abstractmethod
    async def dispatch(self, task: WorkflowTask) -> WorkflowTask:
        """Submit a task for execution and return the updated task."""
        ...


@runtime_checkable
class AgentExecutor(Protocol):
    """Protocol for executing a single task."""

    async def execute(self, task: WorkflowTask) -> TaskResult:
        """Execute the task and return its result."""
        ...


class ExecutionMonitor(abc.ABC):
    """Monitors running workflow state and reacts to changes."""

    @abc.abstractmethod
    async def on_task_completed(
        self, task: WorkflowTask, result: TaskResult, graph: WorkflowGraph,
    ) -> None:
        """Handle task completion."""
        ...

    @abc.abstractmethod
    async def on_task_failed(
        self, task: WorkflowTask, result: TaskResult, graph: WorkflowGraph,
    ) -> None:
        """Handle task failure."""
        ...


class RetryManager(abc.ABC):
    """Manages retry logic for failed tasks."""

    @abc.abstractmethod
    async def should_retry(self, task: WorkflowTask) -> bool:
        """Determine whether a task should be retried."""
        ...

    @abc.abstractmethod
    async def get_backoff(self, task: WorkflowTask) -> float:
        """Return the delay in seconds before the next retry."""
        ...


class ApprovalManager(abc.ABC):
    """Manages human-in-the-loop approval gates."""

    @abc.abstractmethod
    async def request_approval(self, task: WorkflowTask) -> bool:
        """Request human approval for a task. Returns when resolved."""
        ...


class WorkflowEngine(abc.ABC):
    """Central orchestrator for workflow execution."""

    @abc.abstractmethod
    async def execute(self, request: WorkflowRequest) -> WorkflowResult:
        """Run the full workflow lifecycle."""
        ...

    @abc.abstractmethod
    async def pause(self, workflow_id: str) -> None:
        """Pause an active workflow."""
        ...

    @abc.abstractmethod
    async def resume(self, workflow_id: str) -> None:
        """Resume a paused workflow."""
        ...

    @abc.abstractmethod
    async def cancel(self, workflow_id: str) -> None:
        """Cancel an active workflow."""
        ...


class WorkflowService(abc.ABC):
    """Enterprise facade for workflow operations."""

    @abc.abstractmethod
    async def start_workflow(self, request: WorkflowRequest) -> WorkflowResult:
        """Validate, authorise, audit, and start a workflow."""
        ...

    @abc.abstractmethod
    async def get_workflow_status(self, workflow_id: str) -> WorkflowResult | None:
        """Retrieve the current result for a workflow."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# Extension Points — future module integration hooks
# ─────────────────────────────────────────────────────────────────────────────


class MemoryManagerHook(abc.ABC):
    """Extension point for Memory Manager integration.

    Future: called before/after task execution to store/retrieve
    memory context.
    """

    @abc.abstractmethod
    async def on_before_task(self, task: WorkflowTask) -> WorkflowTask:
        """Hook invoked before a task executes."""
        ...

    @abc.abstractmethod
    async def on_after_task(self, task: WorkflowTask, result: TaskResult) -> None:
        """Hook invoked after a task completes."""
        ...


class KnowledgeManagerHook(abc.ABC):
    """Extension point for Knowledge Manager integration.

    Future: retrieves relevant knowledge documents before task
    execution.
    """

    @abc.abstractmethod
    async def enrich_context(self, task: WorkflowTask) -> WorkflowTask:
        """Enrich task inputs with relevant knowledge."""
        ...


class RuleManagerHook(abc.ABC):
    """Extension point for Rule Manager integration.

    Future: evaluates business rules before/after task execution.
    """

    @abc.abstractmethod
    async def evaluate_preconditions(self, task: WorkflowTask) -> bool:
        """Check whether preconditions are met for task execution."""
        ...

    @abc.abstractmethod
    async def evaluate_postconditions(self, task: WorkflowTask, result: TaskResult) -> bool:
        """Validate postconditions after task execution."""
        ...


class ActionEngineHook(abc.ABC):
    """Extension point for Action Engine integration.

    Future: replaces the placeholder executor with real action
    execution capabilities.
    """

    @abc.abstractmethod
    async def execute_action(self, task: WorkflowTask) -> TaskResult:
        """Execute a real action via the Action Engine."""
        ...


class DecisionReviewLayerHook(abc.ABC):
    """Extension point for the Decision Review Layer.

    Future: reviews execution decisions and may override or flag
    decisions for human review.
    """

    @abc.abstractmethod
    async def review_decision(self, decision: WorkflowDecision) -> WorkflowDecision:
        """Review and potentially modify an execution decision."""
        ...


class EvidenceFusionHook(abc.ABC):
    """Extension point for Evidence Fusion.

    Future: fuses evidence from multiple sources (memory, knowledge,
    rules) into a unified context for task execution.
    """

    @abc.abstractmethod
    async def fuse_evidence(self, task: WorkflowTask) -> WorkflowTask:
        """Fuse evidence from all available sources into the task."""
        ...
