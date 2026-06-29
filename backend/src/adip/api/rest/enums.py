"""REST API Layer enumerations."""

from __future__ import annotations

from enum import StrEnum


class OperationStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ErrorType(StrEnum):
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    BUSINESS_ERROR = "business_error"
    PLATFORM_ERROR = "platform_error"
    INTEGRATION_ERROR = "integration_error"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RATE_LIMITED = "rate_limited"
    INTERNAL_ERROR = "internal_error"


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"


class FilterOperator(StrEnum):
    EQ = "eq"
    NEQ = "neq"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    IN = "in"
    NIN = "nin"
    LIKE = "like"
    ILIKE = "ilike"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class ApiVersion(StrEnum):
    V1 = "v1"
    V2 = "v2"


class IdempotencyStatus(StrEnum):
    IN_FLIGHT = "in_flight"
    COMPLETED = "completed"
    EXPIRED = "expired"


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class ComplianceStatus(StrEnum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING = "pending"
    NOT_APPLICABLE = "not_applicable"


class ReadinessStatus(StrEnum):
    READY = "ready"
    NOT_READY = "not_ready"
    DEGRADED = "degraded"


class ExportFormat(StrEnum):
    JSON = "json"
    YAML = "yaml"
    MARKDOWN = "markdown"


class PipelineStage(StrEnum):
    REQUEST = "request"
    VALIDATION = "validation"
    ROUTING = "routing"
    ADAPTER = "adapter"
    RESPONSE = "response"
    MIDDLEWARE = "middleware"
    COMPLIANCE = "compliance"
    QUALITY = "quality"
    DIAGNOSTICS = "diagnostics"
    GOVERNANCE = "governance"
    AUDIT = "audit"
    SNAPSHOT = "snapshot"
    READINESS = "readiness"
