"""EmbeddingManager — generates and manages embeddings for knowledge chunks.

Provider-independent interface with placeholder adapters for OpenAI,
Claude, Local Models, and future providers. No actual API calls.
"""

from __future__ import annotations

import structlog

from adip.knowledge.contracts.models import KnowledgeChunk, KnowledgeEmbedding

log = structlog.get_logger(__name__)


class EmbeddingManager:
    """Generates placeholder embeddings for knowledge chunks."""

    DEFAULT_PROVIDER: str = "placeholder"
    DEFAULT_MODEL: str = "placeholder-model"
    DEFAULT_DIMENSIONS: int = 768

    def __init__(
        self,
        provider: str = DEFAULT_PROVIDER,
        model: str = DEFAULT_MODEL,
        dimensions: int = DEFAULT_DIMENSIONS,
    ) -> None:
        self._provider = provider
        self._model = model
        self._dimensions = dimensions
        self._embeddings: dict[str, KnowledgeEmbedding] = {}

    def embed(self, chunk: KnowledgeChunk) -> KnowledgeEmbedding:
        """Generate a placeholder embedding for a single chunk."""
        log.info(
            "embedding_manager.embed",
            chunk_id=str(chunk.chunk_id),
            provider=self._provider,
        )

        embedding = KnowledgeEmbedding(
            chunk_id=chunk.chunk_id,
            document_id=chunk.document_id,
            provider=self._provider,
            model=self._model,
            dimensions=self._dimensions,
        )
        self._embeddings[str(chunk.chunk_id)] = embedding
        return embedding

    def embed_batch(self, chunks: list[KnowledgeChunk]) -> list[KnowledgeEmbedding]:
        """Generate placeholder embeddings for a batch of chunks."""
        log.info("embedding_manager.embed_batch", count=len(chunks), provider=self._provider)
        return [self.embed(chunk) for chunk in chunks]

    def get_embedding_dimensions(self) -> int:
        """Return the dimensionality of generated embeddings."""
        return self._dimensions

    def get_embedding(self, chunk_id: str) -> KnowledgeEmbedding | None:
        """Retrieve a previously generated embedding by chunk ID."""
        return self._embeddings.get(chunk_id)

    def clear(self) -> None:
        """Clear all stored embeddings."""
        self._embeddings.clear()
