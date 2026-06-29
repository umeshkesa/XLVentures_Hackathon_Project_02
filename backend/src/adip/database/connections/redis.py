"""Redis client factory and dependency helpers.

Usage::

    from adip.database.connections import get_redis

    async with get_redis(config) as client:
        await client.set("key", "value")
"""

from __future__ import annotations

from redis.asyncio import Redis as AsyncRedis

from adip.config.settings import RedisConfig


def create_redis_client(config: RedisConfig) -> AsyncRedis:
    """Build and return an async Redis client from *config*."""
    return AsyncRedis.from_url(
        url=str(config.dsn),
        socket_timeout=config.socket_timeout,
        retry_on_timeout=config.retry_on_timeout,
        decode_responses=True,
    )
