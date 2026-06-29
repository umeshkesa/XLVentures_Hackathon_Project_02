"""Tests for IntegrationHooks."""

from __future__ import annotations

from adip.memory.orchestration.hooks import IntegrationHooks


class TestIntegrationHooks:
    def test_all_hooks_exist(self) -> None:
        hooks = IntegrationHooks()
        assert hasattr(hooks, "on_before_operation")
        assert hasattr(hooks, "on_after_operation")
        assert hasattr(hooks, "planner_hook")
        assert hasattr(hooks, "workflow_hook")
        assert hasattr(hooks, "knowledge_hook")
        assert hasattr(hooks, "rules_hook")
        assert hasattr(hooks, "evidence_hook")
        assert hasattr(hooks, "reasoning_hook")
        assert hasattr(hooks, "recommendation_hook")
        assert hasattr(hooks, "explainability_hook")
        assert hasattr(hooks, "action_hook")
        assert hasattr(hooks, "plugin_hook")

    def test_all_hooks_are_callable(self) -> None:
        hooks = IntegrationHooks()
        import asyncio

        from adip.memory.contracts.models import MemoryRecord, MemoryType
        from adip.memory.enums import MemoryOperation
        for name in [
            "planner_hook", "workflow_hook", "knowledge_hook",
            "rules_hook", "evidence_hook", "reasoning_hook",
            "recommendation_hook", "explainability_hook",
            "action_hook", "plugin_hook",
        ]:
            coro = getattr(hooks, name)()
            asyncio.run(coro)
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        asyncio.run(hooks.on_before_operation(MemoryOperation.CREATE, record))
        asyncio.run(hooks.on_after_operation(MemoryOperation.CREATE, record, record))
