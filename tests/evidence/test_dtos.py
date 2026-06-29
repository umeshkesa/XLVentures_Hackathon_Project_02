"""Tests for Evidence Fusion Engine DTOs."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from adip.evidence.dtos import EvidencePackageDTO, EvidenceRequestDTO, EvidenceResponseDTO
from adip.evidence.enums import EvidenceDomain, EvidenceType

# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceRequestDTO
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceRequestDTO:
    def test_defaults(self) -> None:
        dto = EvidenceRequestDTO()
        assert dto.evidence_type == EvidenceType.KNOWLEDGE
        assert dto.domain == EvidenceDomain.SYSTEM
        assert dto.source_id == ""
        assert dto.correlation_id == ""
        assert dto.parameters == {}

    def test_with_values(self) -> None:
        dto = EvidenceRequestDTO(
            evidence_type=EvidenceType.SENSOR,
            domain=EvidenceDomain.ENERGY,
            source_id="sensor-01",
            correlation_id="corr-1",
            parameters={"interval": "5s"},
        )
        assert dto.evidence_type == EvidenceType.SENSOR
        assert dto.domain == EvidenceDomain.ENERGY
        assert dto.parameters["interval"] == "5s"

    def test_parameters_mutable(self) -> None:
        dto = EvidenceRequestDTO()
        dto.parameters["key"] = "value"
        assert dto.parameters["key"] == "value"

    def test_serialisation(self) -> None:
        dto = EvidenceRequestDTO(evidence_type=EvidenceType.REPORT)
        data = dto.model_dump()
        assert data["evidence_type"] == "REPORT"


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceResponseDTO
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceResponseDTO:
    def test_defaults(self) -> None:
        eid = uuid.uuid4()
        dto = EvidenceResponseDTO(evidence_id=eid, evidence_type=EvidenceType.KNOWLEDGE, domain=EvidenceDomain.SYSTEM)
        assert dto.status == ""
        assert dto.confidence == 0.0
        assert dto.message == ""
        assert dto.metadata == {}

    def test_with_values(self) -> None:
        eid = uuid.uuid4()
        dto = EvidenceResponseDTO(
            evidence_id=eid,
            evidence_type=EvidenceType.SENSOR,
            domain=EvidenceDomain.ENERGY,
            status="COLLECTED",
            confidence=0.9,
            message="Evidence collected successfully",
            metadata={"source": "sensor-01"},
        )
        assert dto.status == "COLLECTED"
        assert dto.confidence == 0.9
        assert dto.message == "Evidence collected successfully"

    def test_evidence_id_required(self) -> None:
        with pytest.raises(ValidationError):
            EvidenceResponseDTO()

    def test_confidence_bounds(self) -> None:
        eid = uuid.uuid4()
        with pytest.raises(ValidationError):
            EvidenceResponseDTO(evidence_id=eid, evidence_type=EvidenceType.KNOWLEDGE, domain=EvidenceDomain.SYSTEM, confidence=1.5)

    def test_serialisation(self) -> None:
        eid = uuid.uuid4()
        dto = EvidenceResponseDTO(evidence_id=eid, evidence_type=EvidenceType.KNOWLEDGE, domain=EvidenceDomain.SYSTEM, status="READY")
        data = dto.model_dump()
        assert data["status"] == "READY"


# ═══════════════════════════════════════════════════════════════════════════════
# EvidencePackageDTO
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidencePackageDTO:
    def test_defaults(self) -> None:
        pid = uuid.uuid4()
        dto = EvidencePackageDTO(package_id=pid)
        assert dto.evidence_count == 0
        assert dto.confidence == 0.0
        assert dto.domains == []
        assert dto.evidence_types == []
        assert dto.metadata == {}

    def test_with_values(self) -> None:
        pid = uuid.uuid4()
        dto = EvidencePackageDTO(
            package_id=pid,
            evidence_count=5,
            confidence=0.85,
            domains=[EvidenceDomain.ENERGY, EvidenceDomain.SECURITY],
            evidence_types=[EvidenceType.SENSOR, EvidenceType.REPORT],
            metadata={"source": "fusion"},
        )
        assert dto.evidence_count == 5
        assert dto.confidence == 0.85
        assert EvidenceDomain.ENERGY in dto.domains
        assert EvidenceType.SENSOR in dto.evidence_types

    def test_package_id_required(self) -> None:
        with pytest.raises(ValidationError):
            EvidencePackageDTO()

    def test_confidence_bounds(self) -> None:
        pid = uuid.uuid4()
        with pytest.raises(ValidationError):
            EvidencePackageDTO(package_id=pid, confidence=1.5)

    def test_serialisation(self) -> None:
        pid = uuid.uuid4()
        dto = EvidencePackageDTO(package_id=pid, evidence_count=3)
        data = dto.model_dump()
        assert data["evidence_count"] == 3
