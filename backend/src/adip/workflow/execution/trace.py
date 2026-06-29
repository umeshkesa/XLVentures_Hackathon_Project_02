"""Observability trace for Workflow Engine pipeline stages.

Re-exports ``WorkflowTrace`` and ``WORKFLOW_VERSION`` from the
contracts layer to preserve backward compatibility for Phase 2
code that imports from ``execution.trace``.
"""

from adip.workflow.contracts.models import WORKFLOW_VERSION, WorkflowTrace

__all__ = ["WORKFLOW_VERSION", "WorkflowTrace"]
