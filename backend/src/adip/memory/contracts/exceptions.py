"""Memory Manager exception hierarchy."""

from __future__ import annotations


class MemoryException(Exception):
    """Base exception for all memory errors."""
    def __init__(self, message: str = "Memory error") -> None:
        self.message = message
        super().__init__(self.message)


class MemoryNotFoundException(MemoryException):
    """Raised when a memory record is not found."""
    def __init__(
        self,
        memory_id: str = "",
        message: str = "",
    ) -> None:
        self.memory_id = memory_id
        if not message:
            message = f"Memory record not found: {memory_id}"
        super().__init__(message)


class MemoryValidationException(MemoryException):
    """Raised when a memory request or record fails validation."""
    def __init__(self, message: str = "Memory validation error") -> None:
        super().__init__(message)


class StorageException(MemoryException):
    """Raised when a storage operation fails."""
    def __init__(
        self,
        tier: str = "",
        message: str = "Storage error",
    ) -> None:
        self.tier = tier
        if tier:
            message = f"Storage error on tier {tier}: {message}"
        super().__init__(message)


class MemoryExpiredException(MemoryException):
    """Raised when an operation is attempted on an expired record."""
    def __init__(
        self,
        memory_id: str = "",
        message: str = "",
    ) -> None:
        self.memory_id = memory_id
        if not message:
            message = f"Memory record has expired: {memory_id}"
        super().__init__(message)


class MemoryPolicyException(MemoryException):
    """Raised when a memory policy is violated."""
    def __init__(
        self,
        policy: str = "",
        message: str = "Memory policy violation",
    ) -> None:
        self.policy = policy
        if policy:
            message = f"Memory policy violation: {policy}"
        super().__init__(message)
