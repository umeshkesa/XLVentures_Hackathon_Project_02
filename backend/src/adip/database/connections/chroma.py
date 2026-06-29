"""ChromaDB client factory.

Usage::

    from adip.database.connections import get_chroma_client

    client = get_chroma_client(config)
    collection = client.get_or_create_collection("my_collection")
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from adip.config.settings import ChromaConfig

if TYPE_CHECKING:
    from chromadb import ClientAPI


def create_chroma_client(config: ChromaConfig) -> ClientAPI:
    """Build and return a ChromaDB client from *config*.

    Uses the HTTP-based client when ``host`` is set (default).
    ``chromadb`` is imported lazily so that this module can be imported
    even when the optional dependency is not installed.
    """
    import chromadb

    return chromadb.HttpClient(
        host=config.host,
        port=config.port,
    )
