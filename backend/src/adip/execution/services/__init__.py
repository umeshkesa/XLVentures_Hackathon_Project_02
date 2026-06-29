"""Services for the Action Engine Phase 3.

Provides the ONLY public API (DefaultExecutionService),
integration hooks, and service infrastructure.
"""

from adip.execution.services.hooks import IntegrationHooks
from adip.execution.services.hooks import hooks as global_hooks
from adip.execution.services.service import DefaultExecutionService

__all__ = [
    "IntegrationHooks",
    "global_hooks",
    "DefaultExecutionService",
]
