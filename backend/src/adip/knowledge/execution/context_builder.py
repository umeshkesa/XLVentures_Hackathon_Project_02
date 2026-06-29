"""ContextBuilder — assembles KnowledgeContext from retrieval results.

Aggregates results, collects domains and document types, estimates
token counts, and enforces context size limits.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeContext, KnowledgeQuery, KnowledgeResult
from adip.knowledge.enums import DocumentType, KnowledgeDomain

log = structlog.get_logger(__name__)


class ContextBuilder:
    """Builds aggregated KnowledgeContext from retrieval results."""

    MAX_RESULTS: int = 50
    MAX_CHUNK_CHARS: int = 100_000

    def build(
        self,
        query: KnowledgeQuery | None = None,
        results: list[KnowledgeResult] | None = None,
    ) -> KnowledgeContext:
        """Build a context from query and results."""
        log.info("context_builder.build", query_present=query is not None, results=len(results) if results else 0)

        results = (results or [])[: self.MAX_RESULTS]

        domains: set[KnowledgeDomain] = set()
        document_types: set[DocumentType] = set()
        total_chars = 0

        for r in results:
            total_chars += len(r.chunk.content)
            domains.add(r.chunk.domain)
            if r.chunk.document_type:
                document_types.add(r.chunk.document_type)

        total_tokens = self._estimate_tokens(total_chars)

        context = KnowledgeContext(
            query=query,
            results=results,
            total_results=len(results),
            domains=list(domains),
            document_types=list(document_types),
            token_count=total_tokens,
            metadata={"max_results": self.MAX_RESULTS, "max_chunk_chars": self.MAX_CHUNK_CHARS},
        )

        if total_chars > self.MAX_CHUNK_CHARS:
            context.metadata["truncated"] = True
            log.info("context_builder.truncated", total_chars=total_chars, max_chars=self.MAX_CHUNK_CHARS)

        log.info("context_builder.build.complete", total_results=len(results), total_tokens=total_tokens)
        return context

    def _estimate_tokens(self, char_count: int) -> int:
        """Rough token estimation (~4 chars per token)."""
        return max(1, char_count // 4)
