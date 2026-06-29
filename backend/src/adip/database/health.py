"""Health-check functions for all ADIP data stores."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from adip.config.settings import ChromaConfig, DatabaseConfig, RedisConfig

logger = structlog.get_logger(__name__)


@dataclass
class HealthStatus:
    """Result of a single health check."""

    name: str
    healthy: bool
    latency_ms: float = 0.0
    error: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


async def check_postgres(
    session: AsyncSession,
    config: DatabaseConfig | None = None,
) -> HealthStatus:
    """Verify PostgreSQL connectivity by executing ``SELECT 1``."""
    import time

    status = HealthStatus(name="postgresql")
    start = time.monotonic()
    try:
        result = await session.execute(text("SELECT 1"))
        row = result.scalar()
        status.healthy = row == 1
        status.details = {"pool_size": config.pool_size} if config else {}
    except Exception as exc:
        status.healthy = False
        status.error = str(exc)
        logger.warning("postgres_health_check_failed", error=str(exc))
    finally:
        status.latency_ms = (time.monotonic() - start) * 1000
    return status


async def check_redis(config: RedisConfig) -> HealthStatus:
    """Verify Redis connectivity by issuing a ``PING``."""
    import time

    from redis.asyncio import Redis as AsyncRedis

    status = HealthStatus(name="redis")
    start = time.monotonic()
    try:
        client = AsyncRedis.from_url(str(config.dsn), socket_timeout=config.socket_timeout)
        pong = await client.ping()
        status.healthy = pong is True
        await client.aclose()
    except Exception as exc:
        status.healthy = False
        status.error = str(exc)
        logger.warning("redis_health_check_failed", error=str(exc))
    finally:
        status.latency_ms = (time.monotonic() - start) * 1000
    return status


async def check_chromadb(config: ChromaConfig) -> HealthStatus:
    """Verify ChromaDB connectivity via the ``heartbeat`` API."""
    import time

    import chromadb

    status = HealthStatus(name="chromadb")
    start = time.monotonic()
    try:
        client = chromadb.HttpClient(host=config.host, port=config.port)
        heartbeat = client.heartbeat()
        status.healthy = isinstance(heartbeat, int) and heartbeat > 0
    except Exception as exc:
        status.healthy = False
        status.error = str(exc)
        logger.warning("chromadb_health_check_failed", error=str(exc))
    finally:
        status.latency_ms = (time.monotonic() - start) * 1000
    return status
