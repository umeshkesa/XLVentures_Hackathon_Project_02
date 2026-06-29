"""Registry Searcher — search framework with composable strategies.

Supports ExactSearch, PrefixSearch, TagSearch, LabelSearch, and
NamespaceSearch strategies. New strategies can be added without
modifying existing code.
"""

from __future__ import annotations

import abc
from typing import Any

import structlog

from adip.registry.contracts.models import RegistryEntry
from adip.registry.execution.models import SearchResult

log = structlog.get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Abstract Strategy
# ─────────────────────────────────────────────────────────────────────────────


class SearchStrategy(abc.ABC):
    """Abstract base for all registry search strategies."""

    @abc.abstractmethod
    def search(
        self,
        query: str,
        entries: list[RegistryEntry],
    ) -> list[SearchResult]:
        """Execute a search against the given entries. Returns scored results."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# Concrete Strategies
# ─────────────────────────────────────────────────────────────────────────────


class ExactSearch(SearchStrategy):
    """Searches for entries whose name matches the query exactly."""

    def search(self, query: str, entries: list[RegistryEntry]) -> list[SearchResult]:
        log.info("registry_searcher.exact_search", query=query)
        results: list[SearchResult] = []
        for entry in entries:
            if entry.name.lower() == query.lower():
                results.append(SearchResult(
                    entry_id=str(entry.entry_id),
                    entry_name=entry.name,
                    score=1.0,
                    strategy="exact",
                ))
        return results


class PrefixSearch(SearchStrategy):
    """Searches for entries whose name starts with the query."""

    def search(self, query: str, entries: list[RegistryEntry]) -> list[SearchResult]:
        log.info("registry_searcher.prefix_search", query=query)
        results: list[SearchResult] = []
        q = query.lower()
        for entry in entries:
            if entry.name.lower().startswith(q):
                score = len(query) / max(len(entry.name), 1)
                results.append(SearchResult(
                    entry_id=str(entry.entry_id),
                    entry_name=entry.name,
                    score=min(score, 1.0),
                    strategy="prefix",
                ))
        return results


class TagSearch(SearchStrategy):
    """Searches for entries that have matching tags."""

    def search(self, query: str, entries: list[RegistryEntry]) -> list[SearchResult]:
        log.info("registry_searcher.tag_search", query=query)
        results: list[SearchResult] = []
        q = query.lower()
        for entry in entries:
            matched_tags = [t for t in entry.tags if q in t.lower()]
            if matched_tags:
                score = len(matched_tags) / max(len(entry.tags), 1)
                results.append(SearchResult(
                    entry_id=str(entry.entry_id),
                    entry_name=entry.name,
                    score=score,
                    strategy="tag",
                ))
        return results


class LabelSearch(SearchStrategy):
    """Searches for entries whose metadata labels match the query."""

    def search(self, query: str, entries: list[RegistryEntry]) -> list[SearchResult]:
        log.info("registry_searcher.label_search", query=query)
        results: list[SearchResult] = []
        q = query.lower()
        for entry in entries:
            for key, value in entry.metadata.items():
                if q in key.lower() or (isinstance(value, str) and q in value.lower()):
                    results.append(SearchResult(
                        entry_id=str(entry.entry_id),
                        entry_name=entry.name,
                        score=0.8,
                        strategy="label",
                    ))
                    break
        return results


class NamespaceSearch(SearchStrategy):
    """Searches for entries within a specific namespace."""

    def __init__(self, namespace: str = "") -> None:
        self.namespace = namespace

    def search(self, query: str, entries: list[RegistryEntry]) -> list[SearchResult]:
        log.info("registry_searcher.namespace_search", query=query, namespace=self.namespace)
        results: list[SearchResult] = []
        ns = self.namespace.lower() if self.namespace else ""
        for entry in entries:
            if ns and entry.namespace.lower() != ns:
                continue
            if not query or query.lower() in entry.name.lower():
                results.append(SearchResult(
                    entry_id=str(entry.entry_id),
                    entry_name=entry.name,
                    score=1.0 if ns else 0.5,
                    strategy="namespace",
                ))
        return results


# ─────────────────────────────────────────────────────────────────────────────
# Strategy Registry & Factory
# ─────────────────────────────────────────────────────────────────────────────

_STRATEGY_REGISTRY: dict[str, type[SearchStrategy]] = {}


def register_strategy(name: str, strategy_cls: type[SearchStrategy]) -> None:
    """Register a new search strategy."""
    _STRATEGY_REGISTRY[name] = strategy_cls
    log.info("registry_searcher.strategy_registered", name=name, cls=strategy_cls.__name__)


def get_strategy(name: str, **kwargs: Any) -> SearchStrategy:
    """Get a search strategy by name with optional kwargs."""
    cls = _STRATEGY_REGISTRY.get(name)
    if cls is None:
        msg = f"Unknown search strategy: {name}. Available: {list(_STRATEGY_REGISTRY)}"
        raise ValueError(msg)
    return cls(**kwargs)


# Register built-in strategies
register_strategy("exact", ExactSearch)
register_strategy("prefix", PrefixSearch)
register_strategy("tag", TagSearch)
register_strategy("label", LabelSearch)
register_strategy("namespace", NamespaceSearch)


# ─────────────────────────────────────────────────────────────────────────────
# RegistrySearcher
# ─────────────────────────────────────────────────────────────────────────────


class RegistrySearcher:
    """Searches the registry using composable search strategies.

    Supports multiple strategies with configurable fallback
    behaviour. Results are deduplicated by entry_id.
    """

    def __init__(self) -> None:
        self._strategies: dict[str, SearchStrategy] = {}

    def register_strategy_instance(self, name: str, strategy: SearchStrategy) -> None:
        """Register a strategy instance for use."""
        self._strategies[name] = strategy
        log.info("registry_searcher.strategy_instance_registered", name=name)

    def search(
        self,
        query: str,
        entries: list[RegistryEntry],
        strategies: list[str] | None = None,
    ) -> list[SearchResult]:
        """Execute search using specified strategies (or all registered)."""
        log.info("registry_searcher.search", query=query)
        strategy_names = strategies or list(self._strategies.keys())
        seen: set[str] = set()
        results: list[SearchResult] = []

        for name in strategy_names:
            strategy = self._strategies.get(name)
            if strategy is None:
                strategy = get_strategy(name)
                self._strategies[name] = strategy
            for result in strategy.search(query, entries):
                if result.entry_id not in seen:
                    seen.add(result.entry_id)
                    results.append(result)

        results.sort(key=lambda r: r.score, reverse=True)
        return results

    def search_by_name(self, name: str, entries: list[RegistryEntry]) -> list[SearchResult]:
        """Search entries by exact name match."""
        log.info("registry_searcher.search_by_name", name=name)
        return ExactSearch().search(name, entries)

    def search_by_tags(self, tags: list[str], entries: list[RegistryEntry]) -> list[SearchResult]:
        """Search entries by tags (entries matching any tag)."""
        log.info("registry_searcher.search_by_tags", tags=tags)
        results: list[SearchResult] = []
        seen: set[str] = set()
        for tag in tags:
            for result in TagSearch().search(tag, entries):
                if result.entry_id not in seen:
                    seen.add(result.entry_id)
                    results.append(result)
        return results

    def count(self, entries: list[RegistryEntry]) -> int:
        """Count total entries."""
        return len(entries)
