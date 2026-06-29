"""Smoke tests for Platform Integration domain models."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from adip.platform.contracts.models import (
    ModuleHealth,
    PlatformHealth,
    PlatformManifest,
    PlatformMetrics,
    PlatformRequest,
    PlatformResponse,
    PlatformTrace,
    PlatformTraceEntry,
    ServiceDescriptor,
)
from adip.platform.enums import (
    ModuleHealthStatus,
    ModuleName,
    PipelineStage,
    PipelineStatus,
)


class TestPlatformRequest:
    def test_defaults(self) -> None:
        r = PlatformRequest()
        assert r.correlation_id == ""
        assert r.pipeline == []
        assert r.payload == {}
        assert r.context == {}
        assert r.metadata == {}

    def test_custom_values(self) -> None:
        r = PlatformRequest(
            correlation_id="corr-123",
            pipeline=[PipelineStage.PLANNER, PipelineStage.MEMORY],
            payload={"input": "test"},
            context={"env": "prod"},
        )
        assert r.correlation_id == "corr-123"
        assert len(r.pipeline) == 2
        assert r.payload["input"] == "test"


class TestPlatformResponse:
    def test_defaults(self) -> None:
        r = PlatformResponse(request_id=uuid.uuid4())
        assert not r.success
        assert r.status == PipelineStatus.PENDING
        assert r.stages_completed == []
        assert r.stages_failed == []
        assert r.errors == []
        assert r.duration_ms == 0.0

    def test_success_response(self) -> None:
        r = PlatformResponse(
            request_id=uuid.uuid4(),
            correlation_id="corr-123",
            success=True,
            status=PipelineStatus.COMPLETED,
            stages_completed=[PipelineStage.PLANNER, PipelineStage.MEMORY],
            output={"result": "ok"},
            duration_ms=42.5,
        )
        assert r.success
        assert r.status == PipelineStatus.COMPLETED
        assert len(r.stages_completed) == 2
        assert r.duration_ms == 42.5


class TestModuleHealth:
    def test_defaults(self) -> None:
        h = ModuleHealth(module=ModuleName.PLANNER)
        assert h.status == ModuleHealthStatus.UNKNOWN
        assert not h.is_registered
        assert h.version == ""
        assert h.message == ""

    def test_custom_values(self) -> None:
        h = ModuleHealth(
            module=ModuleName.ENERGY,
            status=ModuleHealthStatus.HEALTHY,
            is_registered=True,
            version="2.0.0",
            message="All systems operational",
        )
        assert h.status == ModuleHealthStatus.HEALTHY
        assert h.is_registered
        assert h.version == "2.0.0"


class TestPlatformHealth:
    def test_defaults(self) -> None:
        h = PlatformHealth()
        assert h.overall_status == ModuleHealthStatus.UNKNOWN
        assert h.modules == {}
        assert h.healthy_count == 0
        assert h.total_modules == 0

    def test_custom_values(self) -> None:
        planner_health = ModuleHealth(module=ModuleName.PLANNER, status=ModuleHealthStatus.HEALTHY, is_registered=True)
        h = PlatformHealth(
            overall_status=ModuleHealthStatus.HEALTHY,
            modules={"planner": planner_health},
            healthy_count=1,
            total_modules=17,
        )
        assert h.overall_status == ModuleHealthStatus.HEALTHY
        assert h.modules["planner"].is_registered
        assert h.healthy_count == 1


class TestPlatformTraceEntry:
    def test_defaults(self) -> None:
        e = PlatformTraceEntry(stage=PipelineStage.PLANNER)
        assert e.module == ""
        assert e.status == "success"
        assert e.duration_ms == 0.0
        assert e.details == {}

    def test_custom_values(self) -> None:
        e = PlatformTraceEntry(
            stage=PipelineStage.MEMORY,
            module="memory",
            status="failure",
            duration_ms=150.0,
            details={"error": "timeout"},
        )
        assert e.duration_ms == 150.0
        assert e.status == "failure"


class TestPlatformTrace:
    def test_defaults(self) -> None:
        t = PlatformTrace(correlation_id="corr-123")
        assert t.entries == []
        assert t.total_duration_ms == 0.0
        assert not t.completed

    def test_with_entries(self) -> None:
        t = PlatformTrace(
            correlation_id="corr-123",
            entries=[
                PlatformTraceEntry(stage=PipelineStage.PLANNER, duration_ms=10.0),
                PlatformTraceEntry(stage=PipelineStage.MEMORY, duration_ms=20.0),
            ],
            total_duration_ms=30.0,
            completed=True,
        )
        assert len(t.entries) == 2
        assert t.total_duration_ms == 30.0
        assert t.completed


class TestPlatformMetrics:
    def test_defaults(self) -> None:
        m = PlatformMetrics()
        assert m.total_requests == 0
        assert m.successful_requests == 0
        assert m.failed_requests == 0
        assert m.average_duration_ms == 0.0
        assert m.per_stage_counts == {}
        assert m.per_stage_errors == {}

    def test_custom_values(self) -> None:
        m = PlatformMetrics(
            total_requests=100,
            successful_requests=90,
            failed_requests=10,
            average_duration_ms=250.0,
            per_stage_counts={"planner": 100, "memory": 80},
            per_stage_errors={"planner": 5},
        )
        assert m.total_requests == 100
        assert m.successful_requests == 90
        assert m.average_duration_ms == 250.0

    def test_invalid_negative_total(self) -> None:
        with pytest.raises(ValidationError):
            PlatformMetrics(total_requests=-1)


class TestServiceDescriptor:
    def test_defaults(self) -> None:
        d = ServiceDescriptor(name="test_svc", module=ModuleName.API)
        assert d.service_type == ""
        assert d.version == "1.0.0"
        assert d.dependencies == []

    def test_custom_values(self) -> None:
        d = ServiceDescriptor(
            name="planner_service",
            module=ModuleName.PLANNER,
            service_type="PlannerService",
            version="2.0.0",
            dependencies=["auth_service", "memory_service"],
        )
        assert d.name == "planner_service"
        assert len(d.dependencies) == 2


class TestPlatformManifest:
    def test_defaults(self) -> None:
        m = PlatformManifest()
        assert m.platform_version == "1.0.0"
        assert m.modules == []
        assert m.services == []
        assert m.total_services == 0
        assert m.total_modules == 0

    def test_custom_values(self) -> None:
        m = PlatformManifest(
            platform_version="2.0.0",
            modules=[{"name": "planner", "services": [], "service_count": 0}],
            services=[ServiceDescriptor(name="s1", module=ModuleName.PLANNER)],
            total_services=1,
            total_modules=1,
        )
        assert m.platform_version == "2.0.0"
        assert m.total_services == 1
