"""Phase 2 smoke tests — shared context propagation."""

from __future__ import annotations

from adip.platform.orchestration.shared_context import DefaultContextManager


class TestSharedContext:
    """Verify shared context creation and propagation."""

    def test_create_context(self) -> None:
        mgr = DefaultContextManager()
        ctx = mgr.create_context(correlation_id="test-123", trace_id="trace-456")
        assert ctx.correlation_id == "test-123"
        assert ctx.trace_id == "trace-456"
        assert ctx.request_metadata == {}
        assert ctx.domain_context == {}
        assert ctx.execution_context == {}
        assert ctx.session_ids == {}
        assert ctx.module_results == {}

    def test_create_context_with_metadata(self) -> None:
        mgr = DefaultContextManager()
        ctx = mgr.create_context(
            correlation_id="test",
            trace_id="trace",
            metadata={"source": "api", "user": "admin"},
        )
        assert ctx.request_metadata["source"] == "api"
        assert ctx.request_metadata["user"] == "admin"

    def test_create_context_auto_generates_ids(self) -> None:
        mgr = DefaultContextManager()
        ctx = mgr.create_context(correlation_id="", trace_id="")
        assert len(ctx.correlation_id) > 0
        assert len(ctx.trace_id) > 0

    def test_update_context(self) -> None:
        mgr = DefaultContextManager()
        ctx = mgr.create_context("c1", "t1")
        updated = mgr.update_context(ctx, domain_context={"energy": "solar"})
        assert updated.correlation_id == ctx.correlation_id
        assert updated.trace_id == ctx.trace_id
        assert updated.domain_context["energy"] == "solar"

    def test_set_and_get_module_result(self) -> None:
        mgr = DefaultContextManager()
        ctx = mgr.create_context("c1", "t1")
        ctx = mgr.set_module_result(ctx, "planner", {"plan_id": "p-1"})
        ctx = mgr.set_module_result(ctx, "energy", {"decision": "approve"})
        assert mgr.get_module_result(ctx, "planner") == {"plan_id": "p-1"}
        assert mgr.get_module_result(ctx, "energy") == {"decision": "approve"}
        assert mgr.get_module_result(ctx, "unknown") is None

    def test_context_immutability(self) -> None:
        mgr = DefaultContextManager()
        ctx = mgr.create_context("c1", "t1")
        updated = mgr.set_module_result(ctx, "test", {"result": "ok"})
        assert "test" not in ctx.module_results
        assert updated.module_results["test"] == {"result": "ok"}

    def test_update_preserves_existing_results(self) -> None:
        mgr = DefaultContextManager()
        ctx = mgr.create_context("c1", "t1")
        ctx = mgr.set_module_result(ctx, "planner", {"plan_id": "p-1"})
        ctx = mgr.update_context(ctx, domain_context={"energy": "wind"})
        assert mgr.get_module_result(ctx, "planner") == {"plan_id": "p-1"}
        assert ctx.domain_context["energy"] == "wind"
