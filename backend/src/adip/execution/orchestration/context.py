"""ExecutionContextManager — manages execution context for operations.

Deterministic placeholder that assembles and manages contextual
information (asset, machine, facility, workflow) from execution
requests into context models.
"""

from __future__ import annotations

import structlog

from adip.execution.contracts.models import ExecutionContext, ExecutionRequest

log = structlog.get_logger(__name__)


class ExecutionContextManager:
    """Manages execution context for operations.

    Extracts and enriches contextual information from
    ExecutionRequest to provide full execution context.
    """

    def __init__(self) -> None:
        self._contexts: dict[str, ExecutionContext] = {}

    def build(
        self,
        request: ExecutionRequest,
        correlation_id: str = "",
    ) -> ExecutionContext:
        """Build execution context from an execution request.

        Extracts asset, machine, facility, and workflow
        identifiers from the request metadata.

        Args:
            request: The execution request.
            correlation_id: Optional correlation ID.

        Returns:
            ExecutionContext with extracted information.
        """
        meta = request.metadata or {}

        context = ExecutionContext(
            request_id=request.request_id,
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
            cid=correlation_id,
        )
        return context

    def get_context(self, context_id: str) -> ExecutionContext | None:
        """Retrieve a context by ID.

        Args:
            context_id: The context identifier.

        Returns:
            ExecutionContext if found, None otherwise.
        """
        return self._contexts.get(context_id)
