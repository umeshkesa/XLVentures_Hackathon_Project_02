"""Validation tests for Memory Manager DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from adip.memory.contracts.models import MemoryRecord
from adip.memory.enums import MemoryType
from adip.memory.services.dtos import (
    MemoryRequestDTO,
    MemoryResponseDTO,
    MemorySearchRequestDTO,
    MemorySearchResponseDTO,
)


class TestMemoryRequestDTO:
    def test_minimal_creation(self) -> None:
        dto = MemoryRequestDTO(memory_type=MemoryType.SESSION)
        assert dto.memory_type == MemoryType.SESSION
        assert dto.owner_id == ""
        assert dto.namespace == "default"
        assert dto.tags == []
        assert dto.metadata == {}
        assert dto.payload == {}

    def test_custom_values(self) -> None:
        dto = MemoryRequestDTO(
            memory_type=MemoryType.WORKFLOW,
            owner_id="user-1",
            namespace="org-a",
            tags=["important"],
            metadata={"source": "api"},
            payload={"workflow_id": "wf-001"},
        )
        assert dto.owner_id == "user-1"
        assert dto.namespace == "org-a"
        assert dto.payload["workflow_id"] == "wf-001"

    def test_memory_type_required(self) -> None:
        with pytest.raises(ValidationError):
            MemoryRequestDTO()


class TestMemoryResponseDTO:
    def test_default_creation(self) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION)
        dto = MemoryResponseDTO(record=record)
        assert dto.record.memory_id == record.memory_id
        assert dto.tier == ""
        assert dto.duration_ms == 0.0

    def test_custom_values(self) -> None:
        record = MemoryRecord(memory_type=MemoryType.SESSION)
        dto = MemoryResponseDTO(record=record, tier="HOT", duration_ms=5.2)
        assert dto.tier == "HOT"
        assert dto.duration_ms == 5.2


class TestMemorySearchRequestDTO:
    def test_default_creation(self) -> None:
        dto = MemorySearchRequestDTO()
        assert dto.memory_type is None
        assert dto.owner_id == ""
        assert dto.namespace == ""
        assert dto.tags == []
        assert dto.query == ""
        assert dto.limit == 20
        assert dto.offset == 0

    def test_custom_values(self) -> None:
        dto = MemorySearchRequestDTO(
            memory_type=MemoryType.PLANNING,
            owner_id="planner",
            tags=["archived"],
            query="critical path",
            limit=50,
            offset=10,
        )
        assert dto.memory_type == MemoryType.PLANNING
        assert dto.query == "critical path"
        assert dto.limit == 50
        assert dto.offset == 10

    def test_limit_bounds(self) -> None:
        with pytest.raises(ValidationError):
            MemorySearchRequestDTO(limit=0)
        with pytest.raises(ValidationError):
            MemorySearchRequestDTO(limit=1001)

    def test_offset_ge_zero(self) -> None:
        with pytest.raises(ValidationError):
            MemorySearchRequestDTO(offset=-1)


class TestMemorySearchResponseDTO:
    def test_default_creation(self) -> None:
        dto = MemorySearchResponseDTO()
        assert dto.results == []
        assert dto.total_count == 0
        assert dto.limit == 20
        assert dto.offset == 0
        assert dto.duration_ms == 0.0

    def test_custom_values(self) -> None:
        records = [
            MemoryRecord(memory_type=MemoryType.SESSION),
            MemoryRecord(memory_type=MemoryType.WORKFLOW),
        ]
        dto = MemorySearchResponseDTO(
            results=records,
            total_count=2,
            limit=10,
            offset=0,
            duration_ms=3.1,
        )
        assert len(dto.results) == 2
        assert dto.total_count == 2
        assert dto.duration_ms == 3.1
