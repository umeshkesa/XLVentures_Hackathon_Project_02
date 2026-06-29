"""Capability registry exceptions."""

from __future__ import annotations

import uuid


class CapabilityRegistryError(Exception):
    """Base class for capability registry failures."""


class CapabilityAlreadyRegisteredError(CapabilityRegistryError):
    """Raised when a capability ID is registered more than once."""

    def __init__(self, capability_id: uuid.UUID) -> None:
        super().__init__(f"Capability '{capability_id}' is already registered")
        self.capability_id = capability_id


class CapabilityNotFoundError(CapabilityRegistryError):
    """Raised when an update targets an unknown capability ID."""

    def __init__(self, capability_id: uuid.UUID) -> None:
        super().__init__(f"Capability '{capability_id}' was not found")
        self.capability_id = capability_id
