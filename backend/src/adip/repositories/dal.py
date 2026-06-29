"""Central repository access point for one database session."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from enum import StrEnum
from typing import Any, cast

from sqlalchemy.ext.asyncio import AsyncSession

from adip.repositories.contracts import Repository, UserRepositoryPort
from adip.repositories.postgres.user_repository import UserRepository


class RepositoryName(StrEnum):
    """Stable names for repositories exposed by the DAL."""

    USERS = "users"
    WORKFLOWS = "workflows"
    RULES = "rules"
    KNOWLEDGE = "knowledge"
    MEMORIES = "memories"
    RECOMMENDATIONS = "recommendations"
    AUDITS = "audits"


class RepositoryNotConfiguredError(LookupError):
    """Raised when a future repository has not received an adapter yet."""


RepositoryFactory = Callable[[AsyncSession], Repository[Any]]


class DataAccessLayer:
    """Expose repositories sharing the same injected SQLAlchemy session.

    Only the user adapter is concrete today. Future domain repositories are
    registered through factories, avoiding premature storage/schema choices.
    """

    def __init__(
        self,
        session: AsyncSession,
        repository_factories: Mapping[RepositoryName, RepositoryFactory] | None = None,
    ) -> None:
        self._repositories: dict[RepositoryName, Repository[Any]] = {
            RepositoryName.USERS: UserRepository(session)
        }
        for name, factory in (repository_factories or {}).items():
            self._repositories[name] = factory(session)

    @property
    def users(self) -> UserRepositoryPort:
        """Return the user repository."""
        repository = self._repositories[RepositoryName.USERS]
        return cast(UserRepositoryPort, repository)

    def repository(self, name: RepositoryName) -> Repository[Any]:
        """Return a configured repository by its stable domain name."""
        try:
            return self._repositories[name]
        except KeyError as exc:
            raise RepositoryNotConfiguredError(
                f"Repository '{name.value}' has not been configured"
            ) from exc

    @property
    def workflows(self) -> Repository[Any]:
        """Return the configured workflow repository placeholder."""
        return self.repository(RepositoryName.WORKFLOWS)

    @property
    def rules(self) -> Repository[Any]:
        """Return the configured rule repository placeholder."""
        return self.repository(RepositoryName.RULES)

    @property
    def knowledge(self) -> Repository[Any]:
        """Return the configured knowledge repository placeholder."""
        return self.repository(RepositoryName.KNOWLEDGE)

    @property
    def memories(self) -> Repository[Any]:
        """Return the configured memory repository placeholder."""
        return self.repository(RepositoryName.MEMORIES)

    @property
    def recommendations(self) -> Repository[Any]:
        """Return the configured recommendation repository placeholder."""
        return self.repository(RepositoryName.RECOMMENDATIONS)

    @property
    def audits(self) -> Repository[Any]:
        """Return the configured audit repository placeholder."""
        return self.repository(RepositoryName.AUDITS)
