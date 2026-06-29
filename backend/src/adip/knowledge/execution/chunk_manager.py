"""ChunkManager — splits documents into chunks for embedding and retrieval.

Supports placeholder chunking strategies: fixed-size, paragraph,
section, and semantic (future). Maintains chunk-level metadata.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeChunk, KnowledgeDocument

log = structlog.get_logger(__name__)


class ChunkManager:
    """Splits documents into chunks using configurable strategies."""

    DEFAULT_CHUNK_SIZE: int = 500
    DEFAULT_OVERLAP: int = 50

    def chunk_document(
        self,
        document: KnowledgeDocument,
        strategy: str = "fixed",
        chunk_size: int | None = None,
        overlap: int | None = None,
    ) -> list[KnowledgeChunk]:
        """Split a document into chunks using the given strategy."""
        log.info(
            "chunk_manager.chunk_document",
            document_id=str(document.document_id),
            strategy=strategy,
        )

        size = chunk_size or self.DEFAULT_CHUNK_SIZE
        gap = overlap or self.DEFAULT_OVERLAP
        content = document.content

        if strategy == "paragraph":
            chunks = self._chunk_by_paragraph(document, content)
        elif strategy == "fixed":
            chunks = self._chunk_fixed_size(document, content, size, gap)
        else:
            chunks = self._chunk_fixed_size(document, content, size, gap)

        log.info("chunk_manager.chunk_document.complete", document_id=str(document.document_id), chunk_count=len(chunks))
        return chunks

    def get_chunks(self, document_id: str, chunks: list[KnowledgeChunk]) -> list[KnowledgeChunk]:
        """Filter chunks belonging to a document."""
        log.info("chunk_manager.get_chunks", document_id=document_id)
        return [c for c in chunks if str(c.document_id) == document_id]

    def delete_chunks(self, document_id: str, chunks: list[KnowledgeChunk]) -> list[KnowledgeChunk]:
        """Remove all chunks belonging to a document from a list."""
        log.info("chunk_manager.delete_chunks", document_id=document_id)
        return [c for c in chunks if str(c.document_id) != document_id]

    def _chunk_fixed_size(
        self,
        document: KnowledgeDocument,
        content: str,
        chunk_size: int,
        overlap: int,
    ) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        start = 0
        index = 0

        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk_text = content[start:end]

            chunk = KnowledgeChunk(
                document_id=document.document_id,
                document_type=document.document_type,
                domain=document.domain,
                content=chunk_text,
                chunk_index=index,
                token_count=len(chunk_text.split()),
                metadata={"strategy": "fixed", "start": start, "end": end},
                tags=list(document.tags),
            )
            chunks.append(chunk)
            index += 1
            start += max(1, chunk_size - overlap)

        return chunks

    def _chunk_by_paragraph(
        self,
        document: KnowledgeDocument,
        content: str,
    ) -> list[KnowledgeChunk]:
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        chunks: list[KnowledgeChunk] = []

        for i, para in enumerate(paragraphs):
            chunk = KnowledgeChunk(
                document_id=document.document_id,
                document_type=document.document_type,
                domain=document.domain,
                content=para,
                chunk_index=i,
                token_count=len(para.split()),
                metadata={"strategy": "paragraph", "paragraph_index": i},
                tags=list(document.tags),
            )
            chunks.append(chunk)

        return chunks
