"""ExecutionContextBuilder — builds execution context for action plans.

Deterministic placeholder that assembles contextual information
(asset, machine, facility, workflow) from an ActionRequest into
an ActionContext model for downstream execution.
"""

from __future__ import annotations

import structlog

from adip.actions.contracts.models import ActionContext, ActionRequest

log = structlog.get_logger(__name__)


class ExecutionContextBuilder:
    """Builds execution context from action requests.

    Extracts and enriches contextual information from
    ActionRequest to provide full execution context.
    """

    def __init__(self) -> None:
        self._contexts: dict[str, ActionContext] = {}

    def build(
        self,
        request: ActionRequest,
        correlation_id: str = "",
    ) -> ActionContext:
        """Build execution context from an action request.

        Extracts asset, machine, facility, and workflow
        identifiers from the request metadata, and uses
        the request domain and target for context.

        Args:
            request: The action request.
            correlation_id: Optional correlation ID.

        Returns:
            ActionContext with extracted information.
        """
        meta = request.metadata or {}

        context = ActionContext(
            request_id=request.request_id,
            review_decision_id=request.review_decision_id,
            asset_id=meta.get("asset_id", ""),
            machine_id=meta.get("machine_id", ""),
            facility_id=meta.get("facility_id", ""),
            workflow_id=meta.get("workflow_id", ""),
            domain=request.domain,
        )
        self._contexts[str(context.context_id)] = context
        log.info(
            "context.built",
            request_id=str(request.request_id),
            context_id=str(context.context_id),
            domain=request.domain,
        )
        return context

    def get_context(self, context_id: str) -> ActionContext | None:
        """Retrieve a context by ID.

        Args:
            context_id: The context identifier.

        Returns:
            ActionContext if found, None otherwise.
        """
        return self._contexts.get(context_id)

    def clear(self) -> None:
        """Clear all contexts."""
        self._contexts.clear()
