"""Tests for extended MemoryRecord with memory_tier and memory_domain."""

from __future__ import annotations

from uuid import UUID

from adip.memory.contracts.models import (
    ExplainabilityMetadata,
    MemoryRecord,
)
from adip.memory.enums import MemoryDomain, MemoryTier, MemoryType


class TestMemoryRecordExtended:
    def test_default_memory_tier(self) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        assert record.memory_tier == MemoryTier.HOT

    def test_default_memory_domain(self) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        assert record.memory_domain == MemoryDomain.SYSTEM

    def test_custom_memory_tier(self) -> None:
        record = MemoryRecord(
            memory_type=MemoryType.LEARNING,
            owner_id="u1",
            memory_tier=MemoryTier.COLD,
        )
        assert record.memory_tier == MemoryTier.COLD

    def test_custom_memory_domain(self) -> None:
        record = MemoryRecord(
            memory_type=MemoryType.PLANNING,
            owner_id="u1",
            memory_domain=MemoryDomain.PLANNER,
        )
        assert record.memory_domain == MemoryDomain.PLANNER

    def test_all_fields_present(self) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        assert hasattr(record, "memory_id")
        assert hasattr(record, "memory_type")
        assert hasattr(record, "memory_tier")
        assert hasattr(record, "memory_domain")
        assert hasattr(record, "owner_id")
        assert hasattr(record, "namespace")
        assert hasattr(record, "version")
        assert hasattr(record, "created_at")
        assert hasattr(record, "updated_at")
        assert hasattr(record, "metadata")

    def test_memory_id_is_uuid(self) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION, owner_id="u1")
        assert isinstance(record.memory_id, UUID)

    def test_serialization_includes_new_fields(self) -> None:
        record = MemoryRecord(
            memory_type=MemoryType.WORKFLOW,
            owner_id="u1",
            memory_tier=MemoryTier.WARM,
            memory_domain=MemoryDomain.WORKFLOW,
        )
        data = record.model_dump()
        assert data["memory_tier"] == "WARM"
        assert data["memory_domain"] == "WORKFLOW"


class TestExplainabilityMetadata:
    def test_default_empty(self) -> None:
        meta = ExplainabilityMetadata()
        assert meta.why_created == ""
        assert meta.why_updated == ""
        assert meta.why_archived == ""
        assert meta.why_restored == ""
        assert meta.why_deleted == ""
        assert meta.why_expired == ""

    def test_custom_values(self) -> None:
        meta = ExplainabilityMetadata(
            why_created="User request",
            why_updated="System update",
            why_deleted="User cleanup",
        )
        assert meta.why_created == "User request"
        assert meta.why_updated == "System update"
        assert meta.why_deleted == "User cleanup"

    def test_serialization(self) -> None:
        meta = ExplainabilityMetadata(why_created="test")
        data = meta.model_dump()
        assert data["why_created"] == "test"

    def test_triggering_fields_default_empty(self) -> None:
        meta = ExplainabilityMetadata()
        assert meta.triggering_component == ""
        assert meta.triggering_workflow == ""
        assert meta.triggering_user == ""

    def test_triggering_fields_custom_values(self) -> None:
        meta = ExplainabilityMetadata(
            why_created="User request",
            triggering_component="KnowledgeManager",
            triggering_workflow="Workflow-42",
            triggering_user="user-abc",
        )
        assert meta.triggering_component == "KnowledgeManager"
        assert meta.triggering_workflow == "Workflow-42"
        assert meta.triggering_user == "user-abc"

    def test_triggering_fields_serialization(self) -> None:
        meta = ExplainabilityMetadata(
            triggering_component="Planner",
            triggering_user="admin",
        )
        data = meta.model_dump()
        assert data["triggering_component"] == "Planner"
        assert data["triggering_user"] == "admin"
