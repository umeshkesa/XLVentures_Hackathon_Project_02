"""Phase 3.5 smoke tests — Platform Snapshot and Pipeline Version."""

from __future__ import annotations

from adip.platform.enums import ModuleName
from adip.platform.orchestration.pipeline_version import (
    DefaultPlatformPipelineVersionManager,
)
from adip.platform.orchestration.registry import DefaultServiceRegistry
from adip.platform.orchestration.snapshot import DefaultPlatformSnapshotManager


class TestPlatformSnapshotManager:
    """Verify platform snapshot creation."""

    def setup(self) -> DefaultServiceRegistry:
        registry = DefaultServiceRegistry()
        for module in ModuleName:
            registry.register(f"{module.value}_service", object(), module)
        return registry

    def test_create_snapshot(self) -> None:
        registry = self.setup()
        sm = DefaultPlatformSnapshotManager()
        snapshot = sm.create_snapshot(registry, {"planner": "1.0.0", "energy": "2.0.0"})
        assert len(snapshot.snapshot_id) > 0
        assert len(snapshot.services) == len(ModuleName)
        assert len(snapshot.versions) == 2
        assert snapshot.version == "1.0.0"

    def test_snapshot_includes_managers_coordinators(self) -> None:
        registry = self.setup()
        sm = DefaultPlatformSnapshotManager()
        snapshot = sm.create_snapshot(registry, {})
        assert isinstance(snapshot.managers, list)
        assert isinstance(snapshot.coordinators, list)
        assert "total_services" in snapshot.registry
        assert "modules" in snapshot.registry


class TestPipelineVersionManager:
    """Verify pipeline version management."""

    def test_create_version(self) -> None:
        pvm = DefaultPlatformPipelineVersionManager()
        record = pvm.create_version("1.0.0", ["planner", "energy"], 15)
        assert record.pipeline_version == "pipeline-v1"
        assert record.platform_version == "1.0.0"
        assert record.is_active is False
        assert record.stage_count == 15

    def test_activate_version(self) -> None:
        pvm = DefaultPlatformPipelineVersionManager()
        pvm.create_version("1.0.0", ["planner"], 5)
        activated = pvm.activate_version("pipeline-v1")
        assert activated is not None
        assert activated.is_active is True

    def test_activate_nonexistent(self) -> None:
        pvm = DefaultPlatformPipelineVersionManager()
        result = pvm.activate_version("nonexistent")
        assert result is None

    def test_get_active_version(self) -> None:
        pvm = DefaultPlatformPipelineVersionManager()
        assert pvm.get_active_version() is None
        pvm.create_version("1.0.0", ["planner"], 5)
        pvm.activate_version("pipeline-v1")
        active = pvm.get_active_version()
        assert active is not None
        assert active.pipeline_version == "pipeline-v1"

    def test_get_version_history(self) -> None:
        pvm = DefaultPlatformPipelineVersionManager()
        pvm.create_version("1.0.0", ["planner"], 5)
        pvm.create_version("2.0.0", ["planner", "energy"], 10)
        history = pvm.get_version_history()
        assert len(history) == 2
