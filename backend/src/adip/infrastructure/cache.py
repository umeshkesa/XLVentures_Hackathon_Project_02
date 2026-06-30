"""Sync Redis client for domain coordinator caching.

Domain coordinators are synchronous and need a sync Redis client
for caching operations (evidence lookups, knowledge query results, etc.).
"""

from __future__ import annotations

from redis import Redis as SyncRedis

from adip.config.settings import RedisConfig, get_settings

_client: SyncRedis | None = None


def init_redis_cache(config: RedisConfig | None = None) -> None:
    """Initialise the global sync Redis client (call at app startup)."""
    global _client
    cfg = config or get_settings().redis
    _client = SyncRedis.from_url(
        url=str(cfg.dsn),
        socket_timeout=cfg.socket_timeout,
        retry_on_timeout=cfg.retry_on_timeout,
        decode_responses=True,
    )


def get_redis_cache() -> SyncRedis:
    """Return the global sync Redis client.

    Requires :func:`init_redis_cache` to have been called at startup.
    """
    global _client
    if _client is None:
        init_redis_cache()
    return _client


def cache_evidence_list(data: list[dict]) -> None:
    """Cache the full evidence list under a known key with a 5-minute TTL."""
    import json
    try:
        client = get_redis_cache()
        client.setex("evidence:list", 300, json.dumps(data, default=str))
    except Exception:
        pass


def get_cached_evidence_list() -> list[dict] | None:
    """Retrieve cached evidence list, if any."""
    import json
    try:
        client = get_redis_cache()
        raw = client.get("evidence:list")
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return None


def cache_evidence_item(evidence_id: str, data: dict) -> None:
    """Cache a single evidence item with a 10-minute TTL."""
    import json
    try:
        client = get_redis_cache()
        client.setex(f"evidence:{evidence_id}", 600, json.dumps(data, default=str))
    except Exception:
        pass


def get_cached_evidence_item(evidence_id: str) -> dict | None:
    """Retrieve a cached evidence item."""
    import json
    try:
        client = get_redis_cache()
        raw = client.get(f"evidence:{evidence_id}")
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return None


def cache_knowledge_list(data: list[dict]) -> None:
    import json
    try:
        client = get_redis_cache()
        client.setex("knowledge:list", 300, json.dumps(data, default=str))
    except Exception:
        pass


def get_cached_knowledge_list() -> list[dict] | None:
    import json
    try:
        client = get_redis_cache()
        raw = client.get("knowledge:list")
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return None


def invalidate_cache(pattern: str) -> None:
    """Delete all keys matching a glob pattern (e.g. ``evidence:*``)."""
    try:
        client = get_redis_cache()
        for key in client.scan_iter(match=pattern):
            client.delete(key)
    except Exception:
        pass
