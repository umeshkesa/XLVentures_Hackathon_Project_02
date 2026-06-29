"""Standalone, domain-neutral capability registry."""

from adip.registries.capability_registry.exceptions import (
    CapabilityAlreadyRegisteredError,
    CapabilityNotFoundError,
    CapabilityRegistryError,
)
from adip.registries.capability_registry.models import (
    Capability,
    CapabilityQuery,
    CapabilityUpdate,
)
from adip.registries.capability_registry.service import CapabilityRegistry
from adip.registries.capability_registry.storage import (
    CapabilityStorage,
    InMemoryCapabilityStorage,
)

__all__ = [
    "Capability",
    "CapabilityAlreadyRegisteredError",
    "CapabilityNotFoundError",
    "CapabilityQuery",
    "CapabilityRegistry",
    "CapabilityRegistryError",
    "CapabilityStorage",
    "CapabilityUpdate",
    "InMemoryCapabilityStorage",
]
