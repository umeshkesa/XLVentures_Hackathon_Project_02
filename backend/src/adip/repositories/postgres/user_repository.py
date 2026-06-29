"""User repository for data-access operations."""

from __future__ import annotations

from adip.models.user import User
from adip.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """CRUD operations scoped to the ``User`` model."""

    model = User

    async def find_by_email(self, email: str) -> User | None:
        """Return the first user matching *email*, or ``None``."""
        return await self.find_one_by(email=email)

    async def find_by_role(self, role: str) -> list[User]:
        """Return all users assigned a given role."""
        return await self.find_all(role=role)
