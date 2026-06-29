"""ResultFusion — merges retrieval results from multiple strategies.

Removes duplicates, aggregates scores, preserves provenance and
document version information.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeResult

log = structlog.get_logger(__name__)


class ResultFusion:
    """Merges and deduplicates retrieval results."""

    def fuse(self, result_sets: list[list[KnowledgeResult]]) -> list[KnowledgeResult]:
        """Merge multiple result sets into a single deduplicated list."""
        log.info("fusion.fuse", sets=len(result_sets))

        seen_chunks: dict[str, KnowledgeResult] = {}

        for rank_offset, results in enumerate(result_sets):
            for result in results:
                chunk_id = str(result.chunk.chunk_id)
                if chunk_id in seen_chunks:
                    existing = seen_chunks[chunk_id]
                    existing.score = max(existing.score, result.score)
                    existing.metadata["fused"] = True
                    existing.metadata["sources"] = existing.metadata.get("sources", []) + [str(existing.result_id)]
                else:
                    result.metadata["fused"] = False
                    result.metadata["sources"] = [str(result.result_id)]
                    seen_chunks[chunk_id] = result

        fused = sorted(seen_chunks.values(), key=lambda r: r.score, reverse=True)
        for rank, result in enumerate(fused):
            result.rank = rank

        log.info("fusion.fuse.complete", input=sum(len(r) for r in result_sets), output=len(fused))
        return fused
