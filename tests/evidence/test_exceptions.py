"""Tests for Evidence Fusion Engine exceptions."""

from __future__ import annotations

from adip.evidence.contracts.exceptions import (
    EvidenceCorrelationException,
    EvidenceException,
    EvidenceFusionException,
    EvidenceValidationException,
)

# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceException (base)
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceException:
    def test_base_exception(self) -> None:
        exc = EvidenceException()
        assert str(exc) == "Evidence error"
        assert exc.message == "Evidence error"

    def test_base_exception_default_message(self) -> None:
        exc = EvidenceException("Custom error")
        assert str(exc) == "Custom error"


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceValidationException
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceValidationException:
    def test_validation_exception(self) -> None:
        exc = EvidenceValidationException()
        assert str(exc) == "Evidence validation error"

    def test_validation_exception_custom(self) -> None:
        exc = EvidenceValidationException("Missing required fields")
        assert str(exc) == "Missing required fields"


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceCorrelationException
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceCorrelationException:
    def test_correlation_exception_default(self) -> None:
        exc = EvidenceCorrelationException()
        assert str(exc) == "Evidence correlation failed"

    def test_correlation_exception_with_ids(self) -> None:
        exc = EvidenceCorrelationException(
            evidence_id="ev-1",
            correlated_evidence_id="ev-2",
        )
        assert "ev-1" in str(exc)
        assert "ev-2" in str(exc)
        assert exc.evidence_id == "ev-1"
        assert exc.correlated_evidence_id == "ev-2"

    def test_correlation_exception_custom_message(self) -> None:
        exc = EvidenceCorrelationException(message="Custom correlation error")
        assert str(exc) == "Custom correlation error"


# ═══════════════════════════════════════════════════════════════════════════════
# EvidenceFusionException
# ═══════════════════════════════════════════════════════════════════════════════

class TestEvidenceFusionException:
    def test_fusion_exception_default(self) -> None:
        exc = EvidenceFusionException()
        assert str(exc) == "Evidence fusion failed"

    def test_fusion_exception_with_ids(self) -> None:
        exc = EvidenceFusionException(evidence_ids=["ev-1", "ev-2"])
        assert "2" in str(exc)
        assert exc.evidence_ids == ["ev-1", "ev-2"]

    def test_fusion_exception_empty_ids(self) -> None:
        exc = EvidenceFusionException(evidence_ids=[])
        assert str(exc) == "Evidence fusion failed"

    def test_fusion_exception_custom_message(self) -> None:
        exc = EvidenceFusionException(message="Fusion timeout")
        assert str(exc) == "Fusion timeout"


# ═══════════════════════════════════════════════════════════════════════════════
# Exception Hierarchy
# ═══════════════════════════════════════════════════════════════════════════════

class TestExceptionHierarchy:
    def test_exception_hierarchy(self) -> None:
        assert issubclass(EvidenceValidationException, EvidenceException)
        assert issubclass(EvidenceCorrelationException, EvidenceException)
        assert issubclass(EvidenceFusionException, EvidenceException)
        assert issubclass(EvidenceException, Exception)
