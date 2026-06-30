"""Typed, environment-backed configuration for the ADIP backend."""

import os
from functools import lru_cache

from pydantic import BaseModel, Field, PostgresDsn, RedisDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from adip.core.constants import Environment, LogFormat, LogLevel


class AppConfig(BaseModel):
    """Application metadata configuration."""

    name: str = Field(default="ADIP", description="Application display name")
    environment: Environment = Field(
        default=Environment.LOCAL, description="Deployment environment"
    )
    debug: bool = Field(default=False, description="Enable debug mode and detailed error pages")


class ApiConfig(BaseModel):
    """HTTP API server configuration."""

    host: str = Field(default="0.0.0.0", description="Bind address for the HTTP server")
    port: int = Field(default=8000, ge=1, le=65535, description="Bind port for the HTTP server")
    prefix: str = Field(default="/api/v1", description="Global URL prefix for all API routes")
    cors_origins: list[str] = Field(default=["*"], description="Allowed CORS origins")


class DatabaseConfig(BaseModel):
    """Relational database (PostgreSQL) configuration."""

    dsn: PostgresDsn = Field(
        default="postgresql+asyncpg://adip:change-me@localhost:5432/adip",
        description="PostgreSQL connection DSN",
    )
    pool_size: int = Field(default=10, ge=1, description="Database connection pool size")
    max_overflow: int = Field(default=20, ge=0, description="Maximum overflow connections")
    pool_recycle: int = Field(default=3600, ge=1, description="Connection recycle timeout (s)")
    echo: bool = Field(default=False, description="Echo SQL statements to logs")
    migrate: bool = Field(default=True, description="Apply pending migrations on startup")


class RedisConfig(BaseModel):
    """Redis cache and queue configuration."""

    dsn: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis connection DSN",
    )
    socket_timeout: int = Field(default=5, ge=1, description="Socket timeout in seconds")
    retry_on_timeout: bool = Field(default=True, description="Retry operations on timeout")


class ChromaConfig(BaseModel):
    """Vector store (ChromaDB) configuration."""

    host: str = Field(default="localhost", description="ChromaDB host address")
    port: int = Field(default=8000, ge=1, le=65535, description="ChromaDB port")
    collection_name: str = Field(default="adip_embeddings", description="Default collection name")
    embedding_dimension: int = Field(default=1536, ge=1, description="Embedding vector dimension")


class LLMConfig(BaseModel):
    """Large Language Model provider configuration."""

    provider: str = Field(default="openai", description="LLM provider name")
    api_key: SecretStr = Field(
        default=SecretStr("sk-placeholder"), description="LLM provider API key"
    )
    model: str = Field(default="gemini-2.5-flash", description="Model identifier string")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(default=4096, ge=1, description="Maximum tokens per generation")
    timeout: int = Field(default=60, ge=1, description="Request timeout in seconds")


class SecurityConfig(BaseModel):
    """Authentication, authorisation and security configuration."""

    secret_key: SecretStr = Field(
        default=SecretStr("change-me"), description="Secret key used for JWT signing"
    )
    algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    access_token_expire_minutes: int = Field(
        default=30, ge=1, description="Access token lifetime in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, ge=1, description="Refresh token lifetime in days"
    )
    allowed_hosts: list[str] = Field(default=["*"], description="Allowed HTTP Host header values")


class LoggingConfig(BaseModel):
    """Observability and logging configuration."""

    level: LogLevel = Field(default=LogLevel.INFO, description="Log severity level")
    format: LogFormat = Field(default=LogFormat.JSON, description="Log output format")
    include_module: bool = Field(default=True, description="Include module name in log entries")
    file_path: str | None = Field(default=None, description="Path to rotating log file")
    file_max_bytes: int = Field(
        default=10_485_760, ge=1, description="Max log file size before rotation (bytes)"
    )
    file_backup_count: int = Field(
        default=5, ge=0, description="Number of rotated log files to retain"
    )
    otel_enabled: bool = Field(default=False, description="Enable OpenTelemetry tracing")
    otel_endpoint: str | None = Field(default=None, description="OTLP gRPC endpoint")


class Settings(BaseSettings):
    """Validated ADIP runtime settings composed from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="ADIP_",
        env_nested_delimiter="__",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app: AppConfig = AppConfig()
    api: ApiConfig = ApiConfig()
    database: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    chroma: ChromaConfig = ChromaConfig()
    llm: LLMConfig = LLMConfig()
    security: SecurityConfig = SecurityConfig()
    logging: LoggingConfig = LoggingConfig()


@lru_cache
def get_settings() -> Settings:
    """Return cached runtime settings with environment-specific overrides.

    Loads the base ``.env`` file, then optionally overlays ``.env.{environment}``
    so that per-environment secrets or overrides can be kept separate.
    """
    env = os.environ.get("ADIP_APP__ENVIRONMENT", "local")
    env_files = [".env"]
    env_specific = f".env.{env}"
    if os.path.isfile(env_specific):
        env_files.append(env_specific)
    return Settings(_env_file=tuple(env_files))
