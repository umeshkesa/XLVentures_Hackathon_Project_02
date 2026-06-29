"""Tests for Evidence Fusion Engine enums."""

from __future__ import annotations

from adip.evidence.enums import EvidenceDomain, EvidenceStatus, EvidenceType

# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceDomain
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceDomain:
    def test_values(self) -> None:
        assert EvidenceDomain.SYSTEM == "SYSTEM"
        assert EvidenceDomain.ENERGY == "ENERGY"
        assert EvidenceDomain.OPERATIONS == "OPERATIONS"
        assert EvidenceDomain.MAINTENANCE == "MAINTENANCE"
        assert EvidenceDomain.SAFETY == "SAFETY"
        assert EvidenceDomain.CUSTOMER == "CUSTOMER"
        assert EvidenceDomain.COMPLIANCE == "COMPLIANCE"
        assert EvidenceDomain.SECURITY == "SECURITY"
        assert EvidenceDomain.WORKFLOW == "WORKFLOW"
        assert EvidenceDomain.PLANNING == "PLANNING"

    def test_ten_values(self) -> None:
        assert len(EvidenceDomain) == 10

    def test_str_enum(self) -> None:
        assert str(EvidenceDomain.SYSTEM) == "SYSTEM"

    def test_from_string(self) -> None:
        assert EvidenceDomain("ENERGY") == EvidenceDomain.ENERGY


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceType
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceType:
    def test_values(self) -> None:
        assert EvidenceType.KNOWLEDGE == "KNOWLEDGE"
        assert EvidenceType.MEMORY == "MEMORY"
        assert EvidenceType.RULE == "RULE"
        assert EvidenceType.WORKFLOW == "WORKFLOW"
        assert EvidenceType.PLANNER == "PLANNER"
        assert EvidenceType.SENSOR == "SENSOR"
        assert EvidenceType.INCIDENT == "INCIDENT"
        assert EvidenceType.MAINTENANCE == "MAINTENANCE"
        assert EvidenceType.CUSTOMER == "CUSTOMER"
        assert EvidenceType.CRM == "CRM"
        assert EvidenceType.EMAIL == "EMAIL"
        assert EvidenceType.REPORT == "REPORT"

    def test_twelve_values(self) -> None:
        assert len(EvidenceType) == 12

    def test_str_enum(self) -> None:
        assert str(EvidenceType.KNOWLEDGE) == "KNOWLEDGE"

    def test_from_string(self) -> None:
        assert EvidenceType("RULE") == EvidenceType.RULE


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceStatus
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceStatus:
    def test_values(self) -> None:
        assert EvidenceStatus.COLLECTED == "COLLECTED"
        assert EvidenceStatus.VALIDATED == "VALIDATED"
        assert EvidenceStatus.NORMALIZED == "NORMALIZED"
        assert EvidenceStatus.CORRELATED == "CORRELATED"
        assert EvidenceStatus.FUSED == "FUSED"
        assert EvidenceStatus.READY == "READY"

    def test_six_values(self) -> None:
        assert len(EvidenceStatus) == 6

    def test_str_enum(self) -> None:
        assert str(EvidenceStatus.COLLECTED) == "COLLECTED"

    def test_from_string(self) -> None:
        assert EvidenceStatus("FUSED") == EvidenceStatus.FUSED
