"""IntegrationHooks — extension points for ADIP platform services.

Provides hook interfaces for:
    - Planner
    - Workflow Engine
    - Knowledge Manager
    - Rule Manager
    - Evidence Fusion Engine
    - Reasoning Engine
    - Recommendation Engine
    - Explainability Engine
    - Action Engine
    - Plugin Manager

All hooks are placeholders with no implementation.
Future phases will wire these hooks to actual platform services.
"""

from __future__ import annotations

from typing import Any

import structlog

from adip.memory.contracts.models import ExplainabilityMetadata, MemoryRecord
from adip.memory.enums import MemoryOperation

log = structlog.get_logger(__name__)


class IntegrationHooks:
    """Extension hooks for ADIP platform services.

    Each hook is a no-op placeholder.  Implementations will be
    provided in future phases when the corresponding platform
    service is integrated.
    """

    async def on_before_operation(
        self,
        operation: MemoryOperation,
        record: MemoryRecord | None = None,
        **kwargs: Any,
    ) -> None:
        """Called before every memory operation."""
        pass

    async def on_after_operation(
        self,
        operation: MemoryOperation,
        record: MemoryRecord | None = None,
        result: Any = None,
        **kwargs: Any,
    ) -> None:
        """Called after every memory operation."""
        pass

    async def planner_hook(
        self,
        plan_id: str = "",
        memory_id: str = "",
        operation: str = "",
        context: str = "",
        **kwargs: Any,
    ) -> None:
        """Placeholder hook for Planner integration."""  # noqa: DOC501
        pass

    async def workflow_hook(
        self,
        workflow_id: str = "",
        step_id: str = "",
        memory_id: str = "",
        operation: str = "",
        **kwargs: Any,
    ) -> None:
        """Placeholder hook for Workflow Engine integration."""  # noqa: DOC501
        pass

    async def knowledge_hook(
        self,
        knowledge_id: str = "",
        memory_id: str = "",
        operation: str = "",
        **kwargs: Any,
    ) -> None:
        """Placeholder hook for Knowledge Manager integration."""  # noqa: DOC501
        pass

    async def rules_hook(
        self,
        rule_id: str = "",
        memory_id: str = "",
        operation: str = "",
        **kwargs: Any,
    ) -> None:
        """Placeholder hook for Rule Manager integration."""  # noqa: DOC501
        pass

    async def evidence_hook(
        self,
        evidence_id: str = "",
        memory_id: str = "",
        operation: str = "",
        **kwargs: Any,
    ) -> None:
        """Placeholder hook for Evidence Fusion Engine integration."""  # noqa: DOC501
        pass

    async def reasoning_hook(
        self,
        reasoning_id: str = "",
        memory_id: str = "",
        operation: str = "",
        **kwargs: Any,
    ) -> None:
        """Placeholder hook for Reasoning Engine integration."""  # noqa: DOC501
        pass

    async def recommendation_hook(
        self,
        recommendation_id: str = "",
        memory_id: str = "",
        operation: str = "",
        **kwargs: Any,
    ) -> None:
        """Placeholder hook for Recommendation Engine integration."""  # noqa: DOC501
        pass

    async def explainability_hook(
        self,
        memory_id: str = "",
        operation: str = "",
        explainability: ExplainabilityMetadata | None = None,
        **kwargs: Any,
    ) -> None:
        """Placeholder hook for Explainability Engine integration."""  # noqa: DOC501
        pass

    async def action_hook(
        self,
        action_id: str = "",
        memory_id: str = "",
        operation: str = "",
        **kwargs: Any,
    ) -> None:
        """Placeholder hook for Action Engine integration."""  # noqa: DOC501
        pass

    async def plugin_hook(
        self,
        plugin_id: str = "",
        memory_id: str = "",
        operation: str = "",
        **kwargs: Any,
    ) -> None:
        """Placeholder hook for Plugin Manager integration."""  # noqa: DOC501
        pass
