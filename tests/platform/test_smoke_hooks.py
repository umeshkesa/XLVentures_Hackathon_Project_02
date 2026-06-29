"""Smoke tests for platform integration hooks."""

from __future__ import annotations

from adip.platform.enums import PipelineStage
from adip.platform.services.hooks import PlatformHooks


class TestPlatformHooks:
    """Verify hook registration, firing, and exception isolation."""

    def setup_method(self) -> None:
        self.hooks = PlatformHooks()

    def test_register_and_fire_pre_pipeline(self) -> None:
        results: list[str] = []
        self.hooks.register_pre_pipeline(lambda ctx: results.append("pre"))
        self.hooks.fire_pre_pipeline({"key": "val"})
        assert results == ["pre"]

    def test_register_and_fire_post_pipeline(self) -> None:
        results: list[str] = []
        self.hooks.register_post_pipeline(lambda ctx: results.append("post"))
        self.hooks.fire_post_pipeline({"key": "val"})
        assert results == ["post"]

    def test_register_and_fire_pre_stage(self) -> None:
        results: list[str] = []
        self.hooks.register_pre_stage(lambda ctx: results.append(ctx.get("stage", "")))
        self.hooks.fire_pre_stage(PipelineStage.PLANNER, {})
        assert results == ["planner"]

    def test_register_and_fire_post_stage(self) -> None:
        results: list[str] = []
        self.hooks.register_post_stage(lambda ctx: results.append(ctx.get("stage", "")))
        self.hooks.fire_post_stage(PipelineStage.ENERGY, {})
        assert results == ["energy"]

    def test_register_and_fire_on_error(self) -> None:
        results: list[str] = []
        self.hooks.register_on_error(lambda ctx: results.append(ctx.get("error", "")))
        self.hooks.fire_on_error(PipelineStage.MEMORY, "timeout", {})
        assert results == ["timeout"]

    def test_register_and_fire_on_health_check(self) -> None:
        results: list[str] = []
        self.hooks.register_on_health_check(lambda ctx: results.append("health"))
        self.hooks.fire_on_health_check({})
        assert results == ["health"]

    def test_register_and_fire_on_metrics(self) -> None:
        results: list[str] = []
        self.hooks.register_on_metrics(lambda ctx: results.append("metrics"))
        self.hooks.fire_on_metrics({})
        assert results == ["metrics"]

    def test_register_and_fire_on_manifest(self) -> None:
        results: list[str] = []
        self.hooks.register_on_manifest(lambda ctx: results.append("manifest"))
        self.hooks.fire_on_manifest({})
        assert results == ["manifest"]

    def test_multiple_hooks(self) -> None:
        """Verify multiple hooks of the same type all fire."""
        results: list[int] = []
        self.hooks.register_pre_pipeline(lambda ctx: results.append(1))
        self.hooks.register_pre_pipeline(lambda ctx: results.append(2))
        self.hooks.register_pre_pipeline(lambda ctx: results.append(3))
        self.hooks.fire_pre_pipeline({})
        assert results == [1, 2, 3]

    def test_exception_isolation(self) -> None:
        """Verify a failing hook does not prevent other hooks from firing."""
        results: list[str] = []

        def failing_hook(ctx: dict) -> None:
            msg = "intentional hook failure"
            raise RuntimeError(msg)

        def working_hook(ctx: dict) -> None:
            results.append("worked")

        self.hooks.register_pre_pipeline(failing_hook)
        self.hooks.register_pre_pipeline(working_hook)
        self.hooks.fire_pre_pipeline({})
        assert results == ["worked"]

    def test_clear_hooks(self) -> None:
        """Verify clearing all hooks."""
        self.hooks.register_pre_pipeline(lambda ctx: None)
        self.hooks.clear()
        self.hooks.fire_pre_pipeline({})  # Should not raise


class TestGlobalHooks:
    """Verify the global hooks singleton is accessible."""

    def test_global_hooks_importable(self) -> None:
        from adip.platform.services.hooks import hooks
        assert hooks is not None
        assert isinstance(hooks, PlatformHooks)

    def test_global_hooks_works(self) -> None:
        from adip.platform.services.hooks import hooks
        results: list[str] = []
        hooks.register_pre_pipeline(lambda ctx: results.append("global"))
        hooks.fire_pre_pipeline({})
        assert results == ["global"]
        hooks.clear()
