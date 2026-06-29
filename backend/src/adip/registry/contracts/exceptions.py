"""Registry Framework exception hierarchy.

All registry-related exceptions inherit from RegistryException to
ensure consistent error handling across the platform.
"""

from __future__ import annotations


class RegistryException(Exception):
    """Base exception for all registry errors."""

    def __init__(self, message: str = "Registry error") -> None:
        self.message = message
        super().__init__(self.message)


class RegistryValidationException(RegistryException):
    """Raised when a registry operation fails validation."""

    def __init__(self, message: str = "Registry validation error") -> None:
        super().__init__(message)


class RegistryConflictException(RegistryException):
    """Raised when a registry operation causes a conflict."""

    def __init__(
        self,
        entry_id: str = "",
        conflicting_entry_id: str = "",
        message: str = "",
    ) -> None:
        self.entry_id = entry_id
        self.conflicting_entry_id = conflicting_entry_id
        if not message:
            details = []
            if entry_id:
                details.append(f"entry: {entry_id}")
            if conflicting_entry_id:
                details.append(f"conflicts with: {conflicting_entry_id}")
            message = f"Registry conflict detected ({'; '.join(details)})" if details else "Registry conflict detected"
        super().__init__(message)


class RegistrySearchException(RegistryException):
    """Raised when a registry search operation fails."""

    def __init__(
        self,
        query: str = "",
        message: str = "",
    ) -> None:
        self.query = query
        if not message:
            message = f"Registry search failed for query: {query}" if query else "Registry search failed"
        super().__init__(message)
