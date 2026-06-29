"""Evidence caching.

In-memory cache for evidence, bundles, graphs, correlations,
and timelines with configurable TTL.
"""

from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any

from adip.evidence.contracts.models import Evidence
from adip.evidence.execution.graph_builder import EvidenceGraph
from adip.evidence.execution.models import CorrelationResult, EvidenceBundle, Timeline


class CacheEntry:
    """A single entry in the evidence cache."""

    def __init__(self, value: Any, ttl: float) -> None:
        self.value = value
        self.expires_at = time.time() + ttl

    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        return time.time() > self.expires_at


class EvidenceCache:
    """In-memory cache with configurable TTL per type.

    Supports storing and retrieving evidence, bundles, graphs,
    correlations, and timelines.
    """

    def __init__(self, default_ttl: float = 300.0) -> None:
        self._default_ttl = default_ttl
        self._evidence: OrderedDict[str, CacheEntry] = OrderedDict()
        self._bundles: OrderedDict[str, CacheEntry] = OrderedDict()
        self._graphs: OrderedDict[str, CacheEntry] = OrderedDict()
        self._correlations: OrderedDict[str, CacheEntry] = OrderedDict()
        self._timelines: OrderedDict[str, CacheEntry] = OrderedDict()

    def _set(
        self,
        store: OrderedDict[str, CacheEntry],
        key: str,
        value: Any,
        ttl: float | None = None,
    ) -> None:
        store[key] = CacheEntry(value, ttl or self._default_ttl)

    def _get(
        self,
        store: OrderedDict[str, CacheEntry],
        key: str,
    ) -> Any | None:
        entry = store.get(key)
        if entry is None:
            return None
        if entry.is_expired():
            del store[key]
            return None
        store.move_to_end(key)
        return entry.value

    def _delete(
        self,
        store: OrderedDict[str, CacheEntry],
        key: str,
    ) -> bool:
        if key in store:
            del store[key]
            return True
        return False

    def set_evidence(
        self,
        evidence_id: uuid.UUID | str,
        evidence: Evidence,
        ttl: float | None = None,
    ) -> None:
        """Cache a piece of evidence."""
        self._set(self._evidence, str(evidence_id), evidence, ttl)

    def get_evidence(self, evidence_id: uuid.UUID | str) -> Evidence | None:
        """Retrieve a cached evidence item."""
        result = self._get(self._evidence, str(evidence_id))
        return result if isinstance(result, Evidence) else None

    def set_bundle(
        self,
        bundle_id: uuid.UUID | str,
        bundle: EvidenceBundle,
        ttl: float | None = None,
    ) -> None:
        """Cache an evidence bundle."""
        self._set(self._bundles, str(bundle_id), bundle, ttl)

    def get_bundle(self, bundle_id: uuid.UUID | str) -> EvidenceBundle | None:
        """Retrieve a cached bundle."""
        result = self._get(self._bundles, str(bundle_id))
        return result if isinstance(result, EvidenceBundle) else None

    def set_graph(
        self,
        graph_id: str,
        graph: EvidenceGraph,
        ttl: float | None = None,
    ) -> None:
        """Cache an evidence graph."""
        self._set(self._graphs, graph_id, graph, ttl)

    def get_graph(self, graph_id: str) -> EvidenceGraph | None:
        """Retrieve a cached graph."""
        result = self._get(self._graphs, graph_id)
        return result if isinstance(result, EvidenceGraph) else None

    def set_correlation(
        self,
        correlation_id: str,
        correlation: CorrelationResult,
        ttl: float | None = None,
    ) -> None:
        """Cache a correlation result."""
        self._set(self._correlations, correlation_id, correlation, ttl)

    def get_correlation(self, correlation_id: str) -> CorrelationResult | None:
        """Retrieve a cached correlation result."""
        result = self._get(self._correlations, correlation_id)
        return result if isinstance(result, CorrelationResult) else None

    def set_timeline(
        self,
        timeline_id: str,
        timeline: Timeline,
        ttl: float | None = None,
    ) -> None:
        """Cache a timeline."""
        self._set(self._timelines, timeline_id, timeline, ttl)

    def get_timeline(self, timeline_id: str) -> Timeline | None:
        """Retrieve a cached timeline."""
        result = self._get(self._timelines, timeline_id)
        return result if isinstance(result, Timeline) else None

    def invalidate_evidence(self, evidence_id: uuid.UUID | str) -> bool:
        """Remove a cached evidence item."""
        return self._delete(self._evidence, str(evidence_id))

    def invalidate_bundle(self, bundle_id: uuid.UUID | str) -> bool:
        """Remove a cached bundle."""
        return self._delete(self._bundles, str(bundle_id))

    def invalidate_all(self) -> None:
        """Clear all cached data."""
        self._evidence.clear()
        self._bundles.clear()
        self._graphs.clear()
        self._correlations.clear()
        self._timelines.clear()

    def size(self) -> int:
        """Get the total number of cached items."""
        return (
            len(self._evidence)
            + len(self._bundles)
            + len(self._graphs)
            + len(self._correlations)
            + len(self._timelines)
        )
