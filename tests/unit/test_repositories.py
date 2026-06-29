"""Unit tests for repositories, the DAL, and transaction boundaries."""

from __future__ import annotations

import uuid
from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from adip.core.constants import Role
from adip.models.user import User
from adip.repositories.base import BaseRepository
from adip.repositories.contracts import Repository
from adip.repositories.dal import (
    DataAccessLayer,
    RepositoryName,
    RepositoryNotConfiguredError,
)
from adip.repositories.postgres import UserRepository
from adip.repositories.unit_of_work import SqlAlchemyUnitOfWork


def make_session() -> AsyncSession:
    """Build an async-session mock whose coroutine methods can be asserted."""
    return cast(AsyncSession, AsyncMock(spec=AsyncSession))


def make_user() -> User:
    """Build an unpersisted user entity for repository tests."""
    return User(
        email="user@example.com",
        hashed_password="hashed",
        full_name="Test User",
        role=Role.ANALYST,
        is_active=True,
    )


class TestBaseRepository:
    """Verify reusable SQLAlchemy CRUD behavior."""

    @pytest.mark.asyncio
    async def test_find_delegates_to_session_get(self) -> None:
        session = make_session()
        entity_id = uuid.uuid4()
        user = make_user()
        session.get = AsyncMock(return_value=user)
        repository = UserRepository(session)

        result = await repository.find(entity_id)

        assert result is user
        session.get.assert_awaited_once_with(User, entity_id)

    @pytest.mark.asyncio
    async def test_create_flushes_without_committing(self) -> None:
        session = make_session()
        repository = UserRepository(session)

        result = await repository.create(make_user())

        assert isinstance(result, User)
        session.add.assert_called_once_with(result)
        session.flush.assert_awaited_once()
        session.refresh.assert_awaited_once_with(result)
        session.commit.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_delete_missing_entity_is_noop(self) -> None:
        session = make_session()
        session.get = AsyncMock(return_value=None)
        repository = UserRepository(session)

        deleted = await repository.delete(uuid.uuid4())

        assert deleted is False
        session.delete.assert_not_awaited()
        session.flush.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_update_rejects_unknown_model_field(self) -> None:
        session = make_session()
        session.get = AsyncMock(return_value=make_user())
        repository = UserRepository(session)

        with pytest.raises(ValueError, match="Unknown field"):
            await repository.update(uuid.uuid4(), {"not_a_column": "value"})

    @pytest.mark.asyncio
    async def test_pagination_rejects_invalid_bounds(self) -> None:
        repository = BaseRepository[User](make_session())
        repository.model = User

        with pytest.raises(ValueError, match="page must"):
            await repository.paginate(page=0)
        with pytest.raises(ValueError, match="page_size must"):
            await repository.paginate(page_size=0)


class TestDataAccessLayer:
    """Verify centralized and injectable repository access."""

    def test_exposes_concrete_user_repository(self) -> None:
        dal = DataAccessLayer(make_session())

        assert isinstance(dal.users, UserRepository)

    def test_unconfigured_future_repository_fails_clearly(self) -> None:
        dal = DataAccessLayer(make_session())

        with pytest.raises(RepositoryNotConfiguredError, match="workflows"):
            _ = dal.workflows

    def test_future_repository_can_be_injected(self) -> None:
        placeholder = cast(Repository[Any], MagicMock())
        dal = DataAccessLayer(
            make_session(),
            {RepositoryName.WORKFLOWS: lambda _session: placeholder},
        )

        assert dal.workflows is placeholder


class TestSqlAlchemyUnitOfWork:
    """Verify commit, rollback, and cleanup semantics."""

    @pytest.mark.asyncio
    async def test_commit_is_explicit_and_session_is_closed(self) -> None:
        session = make_session()
        factory = cast(async_sessionmaker[AsyncSession], MagicMock(return_value=session))
        unit_of_work = SqlAlchemyUnitOfWork(factory)

        async with unit_of_work:
            assert isinstance(unit_of_work.dal.users, UserRepository)
            await unit_of_work.commit()

        session.commit.assert_awaited_once()
        session.rollback.assert_not_awaited()
        session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_uncommitted_scope_rolls_back(self) -> None:
        session = make_session()
        factory = cast(async_sessionmaker[AsyncSession], MagicMock(return_value=session))

        async with SqlAlchemyUnitOfWork(factory):
            pass

        session.rollback.assert_awaited_once()
        session.close.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_exception_rolls_back_and_propagates(self) -> None:
        session = make_session()
        factory = cast(async_sessionmaker[AsyncSession], MagicMock(return_value=session))

        with pytest.raises(RuntimeError, match="boom"):
            async with SqlAlchemyUnitOfWork(factory):
                raise RuntimeError("boom")

        session.rollback.assert_awaited_once()
        session.close.assert_awaited_once()

    def test_dal_is_unavailable_outside_context(self) -> None:
        factory = cast(async_sessionmaker[AsyncSession], MagicMock())
        unit_of_work = SqlAlchemyUnitOfWork(factory)

        with pytest.raises(RuntimeError, match="must be entered"):
            _ = unit_of_work.dal
