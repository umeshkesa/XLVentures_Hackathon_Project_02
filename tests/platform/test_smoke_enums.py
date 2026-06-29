"""Smoke tests for Platform Integration enums."""

from __future__ import annotations

from enum import StrEnum

from adip.platform.enums import ModuleHealthStatus, ModuleName, PipelineStage, PipelineStatus


class TestModuleName:
    def test_values(self) -> None:
        assert ModuleName.PLANNER == "planner"
        assert ModuleName.WORKFLOW == "workflow"
        assert ModuleName.MEMORY == "memory"
        assert ModuleName.KNOWLEDGE == "knowledge"
        assert ModuleName.RULES == "rules"
        assert ModuleName.PLUGINS == "plugins"
        assert ModuleName.REGISTRY == "registry"
        assert ModuleName.EVIDENCE == "evidence"
        assert ModuleName.REASONING == "reasoning"
        assert ModuleName.RECOMMENDATION == "recommendation"
        assert ModuleName.EXPLAINABILITY == "explainability"
        assert ModuleName.DECISION_REVIEW == "decision_review"
        assert ModuleName.ACTION_MANAGER == "action_manager"
        assert ModuleName.ACTION_ENGINE == "action_engine"
        assert ModuleName.ENERGY == "energy"
        assert ModuleName.API == "api"
        assert ModuleName.AUTH == "auth"

    def test_all_members(self) -> None:
        assert len(ModuleName) == 17

    def test_is_str_enum(self) -> None:
        assert issubclass(ModuleName, StrEnum)


class TestPipelineStage:
    def test_values(self) -> None:
        assert PipelineStage.VALIDATION == "validation"
        assert PipelineStage.PLANNER == "planner"
        assert PipelineStage.WORKFLOW == "workflow"
        assert PipelineStage.MEMORY == "memory"
        assert PipelineStage.KNOWLEDGE == "knowledge"
        assert PipelineStage.RULES == "rules"
        assert PipelineStage.EVIDENCE == "evidence"
        assert PipelineStage.REASONING == "reasoning"
        assert PipelineStage.RECOMMENDATION == "recommendation"
        assert PipelineStage.EXPLAINABILITY == "explainability"
        assert PipelineStage.DECISION_REVIEW == "decision_review"
        assert PipelineStage.ACTION_MANAGER == "action_manager"
        assert PipelineStage.ACTION_ENGINE == "action_engine"
        assert PipelineStage.ENERGY == "energy"
        assert PipelineStage.RESPONSE == "response"

    def test_all_members(self) -> None:
        assert len(PipelineStage) == 15

    def test_is_str_enum(self) -> None:
        assert issubclass(PipelineStage, StrEnum)


class TestPipelineStatus:
    def test_values(self) -> None:
        assert PipelineStatus.PENDING == "pending"
        assert PipelineStatus.RUNNING == "running"
        assert PipelineStatus.COMPLETED == "completed"
        assert PipelineStatus.FAILED == "failed"
        assert PipelineStatus.PARTIAL == "partial"

    def test_all_members(self) -> None:
        assert len(PipelineStatus) == 5

    def test_is_str_enum(self) -> None:
        assert issubclass(PipelineStatus, StrEnum)


class TestModuleHealthStatus:
    def test_values(self) -> None:
        assert ModuleHealthStatus.HEALTHY == "healthy"
        assert ModuleHealthStatus.DEGRADED == "degraded"
        assert ModuleHealthStatus.UNHEALTHY == "unhealthy"
        assert ModuleHealthStatus.UNKNOWN == "unknown"

    def test_all_members(self) -> None:
        assert len(ModuleHealthStatus) == 4

    def test_is_str_enum(self) -> None:
        assert issubclass(ModuleHealthStatus, StrEnum)
