"""QueryAnalyzer — analyses knowledge queries to determine intent, domain,
filters, keywords, and recommended retrieval strategy.

Uses deterministic placeholder logic — no ML or NLP involved.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeQuery
from adip.knowledge.enums import KnowledgeDomain, RetrievalType
from adip.knowledge.execution.models import QueryAnalysis

log = structlog.get_logger(__name__)


class QueryAnalyzer:
    """Analyses knowledge queries to extract search parameters."""

    def analyse(self, query: KnowledgeQuery) -> QueryAnalysis:
        """Analyse a query and return structured analysis results."""
        log.info("query_analyzer.analyse", query_id=str(query.query_id))

        text = query.query_text.lower()
        intent = self._detect_intent(text)
        keywords = [w for w in text.split() if len(w) > 2]

        analysis = QueryAnalysis(
            query_text=query.query_text,
            intent=intent,
            domain=query.domains[0] if query.domains else KnowledgeDomain.SYSTEM,
            filters=self._extract_filters(query),
            keywords=keywords[:20],
            suggested_retrieval_type=self._suggest_retrieval_type(intent),
            requested_version=None,
            confidence=0.8 if keywords else 0.3,
        )
        log.info("query_analyzer.analyse.complete", query_id=str(query.query_id), intent=intent)
        return analysis

    def _detect_intent(self, text: str) -> str:
        if any(w in text for w in ["compare", "difference", "vs", "versus"]):
            return "compare"
        if any(w in text for w in ["summarise", "summary", "overview"]):
            return "summarise"
        if any(w in text for w in ["how", "what is", "what are", "explain"]):
            return "lookup"
        if any(w in text for w in ["list", "find", "search", "show"]):
            return "list"
        return "lookup"

    def _extract_filters(self, query: KnowledgeQuery) -> dict[str, str]:
        filters: dict[str, str] = {}
        if query.namespace:
            filters["namespace"] = query.namespace
        if query.owner_id:
            filters["owner"] = query.owner_id
        return filters

    def _suggest_retrieval_type(self, intent: str) -> RetrievalType:
        if intent in ("summarise", "compare"):
            return RetrievalType.HYBRID
        if intent == "list":
            return RetrievalType.METADATA
        return RetrievalType.VECTOR
