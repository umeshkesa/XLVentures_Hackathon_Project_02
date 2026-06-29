"""Knowledge Manager exception hierarchy.

All knowledge-related exceptions inherit from KnowledgeException
to ensure consistent error handling across the platform.
"""

from __future__ import annotations


class KnowledgeException(Exception):
    """Base exception for all knowledge errors."""

    def __init__(self, message: str = "Knowledge error") -> None:
        self.message = message
        super().__init__(self.message)


class KnowledgeValidationException(KnowledgeException):
    """Raised when a knowledge operation fails validation."""

    def __init__(self, message: str = "Knowledge validation error") -> None:
        super().__init__(message)


class RetrievalException(KnowledgeException):
    """Raised when knowledge retrieval fails."""

    def __init__(
        self,
        query: str = "",
        message: str = "",
    ) -> None:
        self.query = query
        if not message:
            message = f"Knowledge retrieval failed for query: {query}" if query else "Knowledge retrieval failed"
        super().__init__(message)


class IndexException(KnowledgeException):
    """Raised when indexing a document fails."""

    def __init__(
        self,
        document_id: str = "",
        message: str = "",
    ) -> None:
        self.document_id = document_id
        if not message:
            message = f"Indexing failed for document: {document_id}" if document_id else "Indexing failed"
        super().__init__(message)


class EmbeddingException(KnowledgeException):
    """Raised when embedding generation fails."""

    def __init__(
        self,
        chunk_id: str = "",
        message: str = "",
    ) -> None:
        self.chunk_id = chunk_id
        if not message:
            message = f"Embedding generation failed for chunk: {chunk_id}" if chunk_id else "Embedding generation failed"
        super().__init__(message)
