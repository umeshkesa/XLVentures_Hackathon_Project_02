"""Phase 2 smoke tests — platform bootstrap and service resolution."""

from __future__ import annotations

from adip.platform.enums import ModuleName
from adip.platform.orchestration.bootstrap import DefaultPlatformBootstrap


class TestPlatformBootstrap:
    """Verify the platform bootstrap initialises and wires all modules."""

    async def test_initialize_returns_service(self) -> None:
        bootstrap = DefaultPlatformBootstrap()
        service = await bootstrap.initialize()
        assert service is not None
        assert hasattr(service, "execute_pipeline")
        assert hasattr(service, "get_health")
        assert hasattr(service, "get_metrics")
        assert hasattr(service, "get_manifest")

    async def test_initialize_wires_all_modules(self) -> None:
        bootstrap = DefaultPlatformBootstrap()
        await bootstrap.initialize()
        registry = bootstrap.get_registry()
        descriptors = registry.get_service_descriptors()
        module_names = {d.module.value for d in descriptors}
        expected = {m.value for m in ModuleName}
        assert module_names == expected

    async def test_initialize_registers_placeholders(self) -> None:
        bootstrap = DefaultPlatformBootstrap()
        await bootstrap.initialize()
        registry = bootstrap.get_registry()
        planner = registry.resolve("planner_service")
        assert planner is not None
        result = planner.handle_operation("test", {"key": "value"})
        assert result["domain"] == "planner"
        assert result["status"] == "ok"

    async def test_get_service_auto_initializes(self) -> None:
        bootstrap = DefaultPlatformBootstrap()
        service = await bootstrap.get_service()
        assert service is not None
        health = await service.get_health()
        assert health.total_modules == len(ModuleName)

    async def test_get_service_idempotent(self) -> None:
        bootstrap = DefaultPlatformBootstrap()
        s1 = await bootstrap.get_service()
        s2 = await bootstrap.get_service()
        assert s1 is s2

    async def test_bootstrap_pipeline_execution(self) -> None:
        bootstrap = DefaultPlatformBootstrap()
        service = await bootstrap.get_service()
        from adip.platform.contracts.models import PlatformRequest

        request = PlatformRequest(correlation_id="bootstrap-test")
        response = await service.execute_pipeline(request)
        assert response.success
        assert response.status.value == "completed"
        assert len(response.stages_completed) > 0
        assert response.errors == []

    async def test_bootstrap_health(self) -> None:
        bootstrap = DefaultPlatformBootstrap()
        service = await bootstrap.get_service()
        health = await service.get_health()
        assert health.total_modules == len(ModuleName)
        for h in health.modules.values():
            assert h.status.value in ("healthy", "unknown")

    async def test_bootstrap_manifest(self) -> None:
        bootstrap = DefaultPlatformBootstrap()
        service = await bootstrap.get_service()
        manifest = await service.get_manifest()
        assert manifest.total_modules == len(ModuleName)
        assert manifest.total_services == len(ModuleName) * 2  # 2 per module
