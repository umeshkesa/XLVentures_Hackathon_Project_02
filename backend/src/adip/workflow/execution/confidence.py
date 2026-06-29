"""Workflow confidence calculator — separate from Planner confidence.

Evaluates workflow readiness based on graph structure, execution
metrics, and validation results rather than planning quality.
"""

from __future__ import annotations

from adip.workflow.contracts.models import WorkflowGraph, WorkflowMetrics

# Weights for the confidence formula
_GRAPH_DENSITY_WEIGHT: float = 0.25
_CYCLE_FREE_WEIGHT: float = 0.25
_SUCCESS_RATE_WEIGHT: float = 0.30
_RETRY_PENALTY_WEIGHT: float = 0.10
_PARALLEL_EFFICIENCY_WEIGHT: float = 0.10


class WorkflowConfidenceCalculator:
    """Calculates workflow execution confidence.

    The confidence score (0–100) reflects how likely the workflow
    is to execute successfully based on:

    * Graph cyclicity (no cycles = higher confidence)
    * Graph density (too many edges can reduce confidence)
    * Task success rate (from metrics)
    * Retry overhead (penalty for high retry counts)
    * Parallel efficiency (more parallel groups = higher confidence)
    """

    async def calculate(
        self,
        graph: WorkflowGraph,
        metrics: WorkflowMetrics | None = None,
    ) -> float:
        """Compute a confidence score for the given workflow state.

        Returns a float between 0 and 100.
        """
        score = 0.0

        # ── Graph structure ────────────────────────────────────────────
        cycles = graph.detect_cycles()
        cycle_score = 100.0 if not cycles else 0.0
        score += cycle_score * _CYCLE_FREE_WEIGHT

        node_count = len(graph.nodes)
        edge_count = sum(len(deps) for deps in graph.edges.values())
        density = edge_count / max(node_count * (node_count - 1), 1) if node_count > 1 else 0.0
        density_score = max(0.0, 100.0 - (density * 200.0))
        score += density_score * _GRAPH_DENSITY_WEIGHT

        # ── Execution metrics ──────────────────────────────────────────
        if metrics is not None:
            total = metrics.executed_tasks + metrics.successful_tasks
            success_rate = (metrics.successful_tasks / total) * 100.0 if total > 0 else 100.0
            score += success_rate * _SUCCESS_RATE_WEIGHT

            retry_penalty = min(metrics.retry_attempts * 10.0, 100.0)
            score += (100.0 - retry_penalty) * _RETRY_PENALTY_WEIGHT

            parallel_score = min(metrics.parallel_groups * 20.0, 100.0)
            score += parallel_score * _PARALLEL_EFFICIENCY_WEIGHT
        else:
            score += 100.0 * _SUCCESS_RATE_WEIGHT
            score += 100.0 * _RETRY_PENALTY_WEIGHT
            score += 0.0 * _PARALLEL_EFFICIENCY_WEIGHT

        return round(max(0.0, min(100.0, score)), 1)

    async def is_ready(self, graph: WorkflowGraph, metrics: WorkflowMetrics) -> bool:
        """Return ``True`` if the workflow is ready for execution.

        A workflow is considered ready if:
        * The graph has no cycles.
        * There is at least one root node.
        * The confidence score exceeds a minimum threshold (10.0).
        """
        if graph.detect_cycles():
            return False
        if not graph.get_root_nodes():
            return False
        confidence = await self.calculate(graph, metrics)
        return confidence >= 10.0
