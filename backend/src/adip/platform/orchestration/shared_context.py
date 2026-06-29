"""SharedContextManager — typed context propagation across all modules."""

from __future__ import annotations

import uuid
from typing import Any

import structlog

from adip.platform.contracts.models import SharedContext
from adip.platform.interfaces import ContextManager

logger = structlog.get_logger(__name__)


class DefaultContextManager(ContextManager):
    """Default implementation of ContextManager.
    Creates and manages SharedContext instances for pipeline execution.
    Context is immutable — each mutation returns a new instance.
    """

    def create_context(
        self,
        correlation_id: str,
        trace_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> SharedContext:
        ctx = SharedContext(
            correlation_id=correlation_id or str(uuid.uuid4()),
            trace_id=trace_id or str(uuid.uuid4()),
            request_metadata=metadata or {},
        )
        logger.debug("context_manager.created", correlation_id=ctx.correlation_id, trace_id=ctx.trace_id)
        return ctx

    def update_context(self, context: SharedContext, **updates: Any) -> SharedContext:
        return context.model_copy(update=updates)

    def get_module_result(self, context: SharedContext, module: str) -> Any:
        return context.module_results.get(module)

    def set_module_result(self, context: SharedContext, module: str, result: Any) -> SharedContext:
        new_results = dict(context.module_results)
        new_results[module] = result
        return context.model_copy(update={"module_results": new_results})
