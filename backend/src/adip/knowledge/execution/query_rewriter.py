"""QueryRewriter — rewrites queries for improved retrieval.

Placeholder implementation supporting synonym expansion, query
normalisation, and alternative phrasing generation.
"""

from __future__ import annotations

import structlog

from adip.knowledge.execution.models import QueryRewrite

log = structlog.get_logger(__name__)


class QueryRewriter:
    """Rewrites queries to improve retrieval quality."""

    def rewrite(self, query_text: str) -> QueryRewrite:
        """Rewrite a query and return expanded/normalised forms."""
        log.info("query_rewriter.rewrite")

        return QueryRewrite(
            original_query=query_text,
            expanded_query=query_text,
            normalised_query=query_text.strip().lower(),
            alternative_queries=[query_text],
            strategy="none",
        )

    def rewrite_with_synonyms(self, query_text: str, synonyms: dict[str, list[str]] | None = None) -> QueryRewrite:
        """Rewrite a query using synonym expansion."""
        log.info("query_rewriter.rewrite_with_synonyms")

        expanded = query_text
        if synonyms:
            for word, replacements in synonyms.items():
                if word in query_text.lower():
                    expanded += " " + " ".join(replacements)

        return QueryRewrite(
            original_query=query_text,
            expanded_query=expanded,
            normalised_query=query_text.strip().lower(),
            alternative_queries=[query_text, expanded] if expanded != query_text else [query_text],
            strategy="synonym",
        )
