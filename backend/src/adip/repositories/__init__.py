"""Repository layer for data-access abstraction.

All domain repositories should inherit from :class:`adip.repositories.base.BaseRepository`.
"""

from adip.repositories.base import BaseRepository
from adip.repositories.contracts import (
    AuditRepositoryPort,
    KnowledgeRepositoryPort,
    MemoryRepositoryPort,
    RecommendationRepositoryPort,
    Repository,
    RuleRepositoryPort,
    UserRepositoryPort,
    WorkflowRepositoryPort,
)
from adip.repositories.dal import (
    DataAccessLayer,
    RepositoryName,
    RepositoryNotConfiguredError,
)
from adip.repositories.unit_of_work import (
    AbstractUnitOfWork,
    SqlAlchemyUnitOfWork,
    UnitOfWorkFactory,
    create_unit_of_work_factory,
)

__all__ = [
    "AbstractUnitOfWork",
    "AuditRepositoryPort",
    "BaseRepository",
    "DataAccessLayer",
    "KnowledgeRepositoryPort",
    "MemoryRepositoryPort",
    "RecommendationRepositoryPort",
    "Repository",
    "RepositoryName",
    "RepositoryNotConfiguredError",
    "RuleRepositoryPort",
    "SqlAlchemyUnitOfWork",
    "UnitOfWorkFactory",
    "UserRepositoryPort",
    "WorkflowRepositoryPort",
    "create_unit_of_work_factory",
]
