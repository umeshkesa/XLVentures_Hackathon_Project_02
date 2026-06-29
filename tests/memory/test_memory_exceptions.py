"""Validation tests for Memory Manager exceptions."""

from __future__ import annotations

from adip.memory.contracts.exceptions import (
    MemoryException,
    MemoryExpiredException,
    MemoryNotFoundException,
    MemoryPolicyException,
    MemoryValidationException,
    StorageException,
)


class TestMemoryExceptions:
    def test_base_exception(self) -> None:
        exc = MemoryException()
        assert exc.message == "Memory error"
        assert str(exc) == "Memory error"

    def test_base_exception_custom_message(self) -> None:
        exc = MemoryException("Custom error")
        assert exc.message == "Custom error"

    def test_not_found_exception(self) -> None:
        exc = MemoryNotFoundException(memory_id="rec-001")
        assert "rec-001" in str(exc)
        assert exc.memory_id == "rec-001"

    def test_not_found_default(self) -> None:
        exc = MemoryNotFoundException()
        assert "not found" in str(exc).lower()

    def test_validation_exception(self) -> None:
        exc = MemoryValidationException("Invalid policy")
        assert "Invalid policy" in str(exc)

    def test_storage_exception(self) -> None:
        exc = StorageException(tier="HOT", message="Connection failed")
        assert "HOT" in str(exc)
        assert exc.tier == "HOT"

    def test_storage_exception_default(self) -> None:
        exc = StorageException()
        assert str(exc) == "Storage error"

    def test_expired_exception(self) -> None:
        exc = MemoryExpiredException(memory_id="rec-002")
        assert "rec-002" in str(exc)
        assert exc.memory_id == "rec-002"

    def test_expired_exception_default(self) -> None:
        exc = MemoryExpiredException()
        assert "expired" in str(exc).lower()

    def test_policy_exception(self) -> None:
        exc = MemoryPolicyException(policy="encryption_required")
        assert "encryption_required" in str(exc)
        assert exc.policy == "encryption_required"

    def test_policy_exception_default(self) -> None:
        exc = MemoryPolicyException()
        assert "policy" in str(exc).lower()

    def test_all_are_memory_exceptions(self) -> None:
        assert issubclass(MemoryNotFoundException, MemoryException)
        assert issubclass(MemoryValidationException, MemoryException)
        assert issubclass(StorageException, MemoryException)
        assert issubclass(MemoryExpiredException, MemoryException)
        assert issubclass(MemoryPolicyException, MemoryException)
