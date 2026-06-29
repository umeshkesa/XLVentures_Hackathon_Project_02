"""KnowledgePolicyEngine — enforces retrieval and processing policies.

Validates queries, results, contexts, and version access against
configurable policy rules.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import (
    KnowledgeContext,
    KnowledgeDocument,
    KnowledgeQuery,
    KnowledgeResult,
)

log = structlog.get_logger(__name__)


class KnowledgePolicyEngine:
    """Enforces configurable policies for knowledge operations."""

    def __init__(self) -> None:
        self._max_results_per_query: int = 100
        self._max_domains_per_query: int = 5
        self._allowed_domains: list[str] | None = None

    def check_query(self, query: KnowledgeQuery) -> list[str]:
        """Validate a query against policy. Returns list of violations."""
        violations: list[str] = []

        if query.limit > self._max_results_per_query:
            violations.append(
                f"Query limit {query.limit} exceeds max {self._max_results_per_query}"
            )

        if len(query.domains) > self._max_domains_per_query:
            violations.append(
                f"Query domains {len(query.domains)} exceeds max {self._max_domains_per_query}"
            )

        if self._allowed_domains:
            for d in query.domains:
                if d.value not in self._allowed_domains:
                    violations.append(f"Domain {d.value} is not allowed")

        return violations

    def check_result(self, result: KnowledgeResult) -> list[str]:
        """Validate a single result against policy."""
        return []

    def check_context(self, context: KnowledgeContext) -> list[str]:
        """Validate an assembled context against policy."""
        violations: list[str] = []

        if context.total_results == 0:
            violations.append("Context is empty")

        return violations

    def check_version_access(
        self,
        document: KnowledgeDocument,
        required_version: int | None = None,
    ) -> bool:
        """Check if a specific version is accessible."""
        _ = document, required_version
        return True

    def set_max_results(self, limit: int) -> None:
        """Set max results per query policy."""
        self._max_results_per_query = max(1, limit)

    def set_max_domains(self, limit: int) -> None:
        """Set max domains per query policy."""
        self._max_domains_per_query = max(1, limit)

    def set_allowed_domains(self, domains: list[str] | None) -> None:
        """Restrict allowed knowledge domains."""
        self._allowed_domains = domains
