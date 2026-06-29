"""Generic repository base class with common CRUD operations.

Usage::

    from adip.repositories.base import BaseRepository
    from adip.models.base import Base
    from sqlalchemy.orm import Mapped

    class UserModel(Base, AuditMixin):
        email: Mapped[str]

    class UserRepository(BaseRepository[UserModel]):
        model = UserModel
"""

from __future__ import annotations

import uuid
from math import ceil
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from adip.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):  # noqa: UP046
    """Generic CRUD repository for SQLAlchemy ORM models.

    Subclass and set ``model`` to the desired ORM class::

        class UserRepository(BaseRepository[UserModel]):
            model = UserModel
    """

    model: type[T]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ── Query helpers ──────────────────────────────────────────────────

    def _stmt(self) -> Select[tuple[T]]:
        return select(self.model)

    # ── Read ───────────────────────────────────────────────────────────

    async def find(self, id: uuid.UUID) -> T | None:
        """Return a single record by primary key, or ``None``."""
        return await self.session.get(self.model, id)

    async def find_one_by(self, **filters: Any) -> T | None:
        """Return the first record matching *filters*, or ``None``."""
        stmt = self._stmt().filter_by(**filters)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all(self, **filters: Any) -> list[T]:
        """Return all records matching *filters* (unpaginated)."""
        stmt = self._stmt().filter_by(**filters)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def paginate(
        self,
        page: int = 1,
        page_size: int = 20,
        **filters: Any,
    ) -> tuple[list[T], int, int]:
        """Return a page of records and the total count.

        Returns ``(items, total_count, total_pages)``.
        """
        if page < 1:
            raise ValueError("page must be greater than or equal to 1")
        if page_size < 1:
            raise ValueError("page_size must be greater than or equal to 1")
        base_stmt = self._stmt().filter_by(**filters)

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total: int = (await self.session.execute(count_stmt)).scalar() or 0

        total_pages = max(1, ceil(total / page_size)) if total else 1
        offset = (page - 1) * page_size
        page_stmt = base_stmt.offset(offset).limit(page_size)
        result = await self.session.execute(page_stmt)
        items = list(result.scalars().all())

        return items, total, total_pages

    # ── Create ─────────────────────────────────────────────────────────

    async def create(self, data: T | dict[str, Any] | BaseModel) -> T:
        """Persist a new record and return it."""
        if isinstance(data, BaseModel):
            data = data.model_dump()
        instance = self.model(**data) if isinstance(data, dict) else data
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    # ── Update ─────────────────────────────────────────────────────────

    async def update(self, id: uuid.UUID, data: dict[str, Any] | BaseModel) -> T | None:
        """Partially update a record by primary key and return the updated version.

        Returns ``None`` if the record does not exist.
        """
        if isinstance(data, BaseModel):
            data = data.model_dump(exclude_unset=True)
        instance = await self.find(id)
        if instance is None:
            return None
        for field, value in data.items():
            if not hasattr(self.model, field):
                raise ValueError(f"Unknown field '{field}' for {self.model.__name__}")
            setattr(instance, field, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    # ── Delete ─────────────────────────────────────────────────────────

    async def delete(self, id: uuid.UUID) -> bool:
        """Delete a record by primary key.  Returns ``True`` if a row was removed."""
        instance = await self.find(id)
        if instance is None:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def bulk_create(self, instances: list[T]) -> list[T]:
        """Persist multiple records in a single flush."""
        self.session.add_all(instances)
        await self.session.flush()
        for inst in instances:
            await self.session.refresh(inst)
        return instances
