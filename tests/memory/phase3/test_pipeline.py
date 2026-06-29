"""Tests for MemoryOperationPipeline."""

from __future__ import annotations

from adip.memory.enums import MemoryOperation
from adip.memory.orchestration.pipeline import MemoryOperationPipeline


class TestMemoryOperationPipeline:
    def test_default_stages(self) -> None:
        assert len(MemoryOperationPipeline.STAGES) == 12

    def test_record_stage(self) -> None:
        pipeline = MemoryOperationPipeline()
        pipeline.record_stage("MemoryService", MemoryOperation.CREATE, "id-1")
        stages = pipeline.get_executed_stages()
        assert len(stages) == 1
        assert stages[0]["stage"] == "MemoryService"
        assert stages[0]["operation"] == "CREATE"

    def test_validate_pipeline_all_stages(self) -> None:
        pipeline = MemoryOperationPipeline()
        for stage in MemoryOperationPipeline.STAGES:
            pipeline.record_stage(stage, MemoryOperation.READ)
        missing = pipeline.validate_pipeline()
        assert missing == []

    def test_validate_pipeline_missing_stages(self) -> None:
        pipeline = MemoryOperationPipeline()
        pipeline.record_stage("MemoryService", MemoryOperation.CREATE)
        missing = pipeline.validate_pipeline()
        assert len(missing) == 11

    def test_clear(self) -> None:
        pipeline = MemoryOperationPipeline()
        pipeline.record_stage("MemoryService", MemoryOperation.CREATE)
        pipeline.clear()
        assert pipeline.get_executed_stages() == []

    def test_stage_order(self) -> None:
        pipeline = MemoryOperationPipeline()
        pipeline.record_stage("MemoryService", MemoryOperation.CREATE)
        pipeline.record_stage("MemoryManager", MemoryOperation.CREATE)
        stages = pipeline.get_executed_stages()
        assert stages[0]["order"] == 0
        assert stages[1]["order"] == 1
