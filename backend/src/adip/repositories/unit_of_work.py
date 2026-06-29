"""Unit-of-work abstractions and SQLAlchemy implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from adip.repositories.dal import DataAccessLayer, RepositoryFactory, RepositoryName


class AbstractUnitOfWork(ABC):
    """Transaction boundary consumed by application services."""

    @property
    @abstractmethod
    def dal(self) -> DataAccessLayer:
        """Return repositories participating in this transaction."""

    @abstractmethod
    async def __aenter__(self) -> AbstractUnitOfWork:
        """Open the transaction scope."""

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the transaction scope, rolling back when necessary."""

    @abstractmethod
    async def commit(self) -> None:
        """Commit changes made in this unit of work."""

    @abstractmethod
    async def rollback(self) -> None:
        """Discard changes made in this unit of work."""


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """Manage a SQLAlchemy session and its repository collection."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        repository_factories: Mapping[RepositoryName, RepositoryFactory] | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._repository_factories = repository_factories
        self._session: AsyncSession | None = None
        self._dal: DataAccessLayer | None = None
        self._committed = False

    @property
    def dal(self) -> DataAccessLayer:
        """Return the DAL after entering the async context."""
        if self._dal is None:
            raise RuntimeError("Unit of work must be entered before accessing repositories")
        return self._dal

    async def __aenter__(self) -> SqlAlchemyUnitOfWork:
        """Create the session and session-scoped DAL."""
        if self._session is not None:
            raise RuntimeError("Unit of work is already active")
        self._session = self._session_factory()
        self._dal = DataAccessLayer(self._session, self._repository_factories)
        self._committed = False
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Rollback uncommitted work and always release the session."""
        session = self._require_session()
        try:
            if exc_type is not None or not self._committed:
                await session.rollback()
        finally:
            await session.close()
            self._session = None
            self._dal = None
            self._committed = False

    async def commit(self) -> None:
        """Commit the active transaction explicitly."""
        await self._require_session().commit()
        self._committed = True

    async def rollback(self) -> None:
        """Rollback the active transaction explicitly."""
        await self._require_session().rollback()
        self._committed = False

    def _require_session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Unit of work is not active")
        return self._session


UnitOfWorkFactory = Callable[[], AbstractUnitOfWork]


def create_unit_of_work_factory(
    session_factory: async_sessionmaker[AsyncSession],
    repository_factories: Mapping[RepositoryName, RepositoryFactory] | None = None,
) -> UnitOfWorkFactory:
    """Create an injectable factory for transaction-scoped units of work."""

    def factory() -> AbstractUnitOfWork:
        return SqlAlchemyUnitOfWork(session_factory, repository_factories)

    return factory
