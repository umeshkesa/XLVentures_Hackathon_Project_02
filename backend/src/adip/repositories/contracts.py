"""Persistence ports used by the data-access layer.

The protocols in this module belong to the application boundary. Concrete
storage adapters may use PostgreSQL, MongoDB, ChromaDB, Redis, or an in-memory
implementation without changing their consumers.
"""

from __future__ import annotations

import uuid
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

from adip.models.base import Base
from adip.models.user import User

EntityT = TypeVar("EntityT", bound=Base)


class Repository(Protocol[EntityT]):
    """Storage-agnostic CRUD contract for one entity type."""

    async def find(self, id: uuid.UUID) -> EntityT | None:
        """Return an entity by identifier, if it exists."""
        ...

    async def find_one_by(self, **filters: Any) -> EntityT | None:
        """Return at most one entity matching the supplied filters."""
        ...

    async def find_all(self, **filters: Any) -> list[EntityT]:
        """Return all entities matching the supplied filters."""
        ...

    async def create(self, data: EntityT | dict[str, Any] | BaseModel) -> EntityT:
        """Add an entity to the current unit of work."""
        ...

    async def update(
        self, id: uuid.UUID, data: dict[str, Any] | BaseModel
    ) -> EntityT | None:
        """Update an entity in the current unit of work."""
        ...

    async def delete(self, id: uuid.UUID) -> bool:
        """Remove an entity from the current unit of work."""
        ...


class UserRepositoryPort(Repository[User], Protocol):
    """Repository contract for users."""

    async def find_by_email(self, email: str) -> User | None:
        """Return a user by email address."""
        ...


class WorkflowRepositoryPort(Repository[EntityT], Protocol[EntityT]):
    """Placeholder persistence port for future workflow entities."""


class RuleRepositoryPort(Repository[EntityT], Protocol[EntityT]):
    """Placeholder persistence port for future rule entities."""


class KnowledgeRepositoryPort(Repository[EntityT], Protocol[EntityT]):
    """Placeholder persistence port for future knowledge entities."""


class MemoryRepositoryPort(Repository[EntityT], Protocol[EntityT]):
    """Placeholder persistence port for future memory entities."""


class RecommendationRepositoryPort(Repository[EntityT], Protocol[EntityT]):
    """Placeholder persistence port for future recommendation entities."""


class AuditRepositoryPort(Repository[EntityT], Protocol[EntityT]):
    """Placeholder persistence port for future audit entities."""
