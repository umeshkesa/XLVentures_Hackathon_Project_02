"""Tests for REST API models — response wrapper, error models, pagination, filtering, sorting."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from adip.api.rest.enums import (
    ApiVersion,
    ErrorType,
    FilterOperator,
    IdempotencyStatus,
    OperationStatus,
    SortDirection,
)
from adip.api.rest.models import (
    ApiError,
    ApiMetadata,
    ApiResponse,
    ApiVersionInfo,
    AuthenticationError,
    AuthorizationError,
    BusinessError,
    ErrorDetail,
    FilterCriteria,
    FilterGroup,
    FilterParams,
    HealthResponse,
    IdempotencyKey,
    IdempotencyRecord,
    IntegrationError,
    LiveResponse,
    OperationRequest,
    OperationResult,
    OperationStatusResponse,
    PaginatedResponse,
    PaginationParams,
    PaginationResult,
    PlatformError,
    RateLimitConfig,
    RateLimitHeaders,
    RateLimitPolicy,
    ReadyResponse,
    ResponseWrapper,
    SortCriteria,
    SortParams,
    VersionResponse,
)
from adip.api.rest.models import (
    ValidationError as ValidationErrorModel,
)


class TestEnums:
    def test_operation_status_values(self) -> None:
        assert OperationStatus.PENDING.value == "pending"
        assert OperationStatus.RUNNING.value == "running"
        assert OperationStatus.COMPLETED.value == "completed"
        assert OperationStatus.FAILED.value == "failed"
        assert OperationStatus.CANCELLED.value == "cancelled"

    def test_error_type_values(self) -> None:
        assert ErrorType.VALIDATION_ERROR.value == "validation_error"
        assert ErrorType.AUTHENTICATION_ERROR.value == "authentication_error"
        assert ErrorType.AUTHORIZATION_ERROR.value == "authorization_error"
        assert ErrorType.BUSINESS_ERROR.value == "business_error"
        assert ErrorType.PLATFORM_ERROR.value == "platform_error"
        assert ErrorType.INTEGRATION_ERROR.value == "integration_error"

    def test_sort_direction_values(self) -> None:
        assert SortDirection.ASC.value == "asc"
        assert SortDirection.DESC.value == "desc"

    def test_filter_operator_values(self) -> None:
        assert FilterOperator.EQ.value == "eq"
        assert FilterOperator.IN.value == "in"
        assert FilterOperator.LIKE.value == "like"

    def test_api_version_values(self) -> None:
        assert ApiVersion.V1.value == "v1"
        assert ApiVersion.V2.value == "v2"

    def test_idempotency_status_values(self) -> None:
        assert IdempotencyStatus.IN_FLIGHT.value == "in_flight"
        assert IdempotencyStatus.COMPLETED.value == "completed"
        assert IdempotencyStatus.EXPIRED.value == "expired"


class TestApiMetadata:
    def test_default_creation(self) -> None:
        meta = ApiMetadata()
        assert isinstance(meta.timestamp, datetime)
        assert meta.version.api_version == ApiVersion.V1
        assert meta.trace_id is not None
        assert meta.processing_time_ms is None

    def test_custom_values(self) -> None:
        meta = ApiMetadata(
            timestamp=datetime(2026, 1, 1),
            version=ApiVersionInfo(version="2.0.0", api_version=ApiVersion.V2),
            trace_id="custom-trace",
            processing_time_ms=42.5,
        )
        assert meta.timestamp.year == 2026
        assert meta.version.api_version == ApiVersion.V2
        assert meta.trace_id == "custom-trace"
        assert meta.processing_time_ms == 42.5


class TestApiError:
    def test_default_creation(self) -> None:
        error = ApiError(code="test_error", message="Test message")
        assert error.code == "test_error"
        assert error.message == "Test message"
        assert error.details is None
        assert error.errors is None

    def test_with_details(self) -> None:
        error = ApiError(
            code="test_error",
            message="Test message",
            details={"field": "name"},
            errors=[ErrorDetail(code="required", message="Field is required", field="name")],
        )
        assert error.details == {"field": "name"}
        assert len(error.errors) == 1
        assert error.errors[0].field == "name"


class TestApiResponse:
    def test_default_success(self) -> None:
        response = ApiResponse()
        assert response.success is True
        assert response.data is None
        assert response.errors is None

    def test_with_data(self) -> None:
        response = ApiResponse(data={"key": "value"})
        assert response.success is True
        assert response.data == {"key": "value"}

    def test_with_errors(self) -> None:
        error = ApiError(code="not_found", message="Resource not found")
        response = ApiResponse(success=False, errors=[error])
        assert response.success is False
        assert len(response.errors) == 1
        assert response.errors[0].code == "not_found"

    def test_trace_id_and_timestamp_copy(self) -> None:
        meta = ApiMetadata(trace_id="test-trace")
        response = ApiResponse(metadata=meta)
        assert response.trace_id == "test-trace"
        assert response.timestamp == meta.timestamp


class TestErrorModels:
    def test_validation_error(self) -> None:
        err = ValidationErrorModel()
        assert err.type == ErrorType.VALIDATION_ERROR
        assert err.code == "validation_error"

    def test_authentication_error(self) -> None:
        err = AuthenticationError()
        assert err.type == ErrorType.AUTHENTICATION_ERROR
        assert err.code == "authentication_error"

    def test_authorization_error(self) -> None:
        err = AuthorizationError()
        assert err.type == ErrorType.AUTHORIZATION_ERROR
        assert err.code == "authorization_error"

    def test_business_error(self) -> None:
        err = BusinessError()
        assert err.type == ErrorType.BUSINESS_ERROR
        assert err.code == "business_error"

    def test_platform_error(self) -> None:
        err = PlatformError()
        assert err.type == ErrorType.PLATFORM_ERROR
        assert err.code == "platform_error"

    def test_integration_error(self) -> None:
        err = IntegrationError()
        assert err.type == ErrorType.INTEGRATION_ERROR
        assert err.code == "integration_error"


class TestPagination:
    def test_pagination_params_defaults(self) -> None:
        params = PaginationParams()
        assert params.limit == 100
        assert params.offset == 0
        assert params.page is None
        assert params.page_size is None

    def test_pagination_params_validation(self) -> None:
        with pytest.raises(ValidationError):
            PaginationParams(limit=0)

        with pytest.raises(ValidationError):
            PaginationParams(limit=1001)

    def test_pagination_result(self) -> None:
        result = PaginationResult(limit=10, offset=0, total=100)
        assert result.limit == 10
        assert result.offset == 0
        assert result.total == 100
        assert result.page is None
        assert result.total_pages is None

    def test_paginated_response(self) -> None:
        response = PaginatedResponse(
            items=[1, 2, 3],
            pagination=PaginationResult(limit=10, offset=0, total=3),
        )
        assert len(response.items) == 3
        assert response.pagination.total == 3


class TestFiltering:
    def test_filter_criteria(self) -> None:
        criteria = FilterCriteria(field="name", operator=FilterOperator.EQ, value="test")
        assert criteria.field == "name"
        assert criteria.operator == FilterOperator.EQ
        assert criteria.value == "test"

    def test_filter_group(self) -> None:
        group = FilterGroup(
            filters=[FilterCriteria(field="age", operator=FilterOperator.GT, value=18)],
            combinator="AND",
        )
        assert len(group.filters) == 1
        assert group.combinator == "AND"

    def test_filter_group_invalid_combinator(self) -> None:
        with pytest.raises(ValidationError):
            FilterGroup(combinator="XOR")

    def test_filter_params(self) -> None:
        params = FilterParams(raw="name eq 'test'")
        assert params.raw == "name eq 'test'"
        assert params.groups == []


class TestSorting:
    def test_sort_criteria(self) -> None:
        criteria = SortCriteria(field="name", direction=SortDirection.DESC)
        assert criteria.field == "name"
        assert criteria.direction == SortDirection.DESC

    def test_sort_params(self) -> None:
        params = SortParams(
            sorts=[
                SortCriteria(field="name"),
                SortCriteria(field="age", direction=SortDirection.DESC),
            ]
        )
        assert len(params.sorts) == 2
        assert params.sorts[0].direction == SortDirection.ASC
        assert params.sorts[1].direction == SortDirection.DESC


class TestHealthModels:
    def test_health_response(self) -> None:
        resp = HealthResponse(status="healthy")
        assert resp.status == "healthy"
        assert resp.version is not None
        assert isinstance(resp.timestamp, datetime)

    def test_ready_response(self) -> None:
        resp = ReadyResponse(ready=True)
        assert resp.ready is True

    def test_live_response(self) -> None:
        resp = LiveResponse(alive=True)
        assert resp.alive is True

    def test_version_response(self) -> None:
        resp = VersionResponse(version="1.2.3")
        assert resp.version == "1.2.3"


class TestIdempotency:
    def test_idempotency_key(self) -> None:
        key = IdempotencyKey(key="abc-123")
        assert key.key == "abc-123"
        assert key.header_name == "Idempotency-Key"

    def test_idempotency_record(self) -> None:
        record = IdempotencyRecord(key="abc-123")
        assert record.key == "abc-123"
        assert record.status == IdempotencyStatus.IN_FLIGHT


class TestAsyncOperation:
    def test_operation_request(self) -> None:
        req = OperationRequest(operation_type="data_export")
        assert req.operation_type == "data_export"
        assert req.params == {}

    def test_operation_status_response(self) -> None:
        resp = OperationStatusResponse(operation_type="data_export")
        assert resp.status == OperationStatus.PENDING
        assert resp.progress is None

    def test_operation_result(self) -> None:
        result = OperationResult(operation_id="00000000-0000-0000-0000-000000000001")
        assert result.status == OperationStatus.COMPLETED


class TestRateLimit:
    def test_rate_limit_config(self) -> None:
        config = RateLimitConfig()
        assert config.requests_per_second == 10
        assert config.burst_size == 20
        assert config.enabled is True

    def test_rate_limit_headers(self) -> None:
        headers = RateLimitHeaders(limit=100, remaining=50, reset=1234567890)
        assert headers.limit == 100
        assert headers.remaining == 50

    def test_rate_limit_policy(self) -> None:
        policy = RateLimitPolicy(name="default")
        assert policy.name == "default"
        assert policy.routes == []


class TestResponseWrapper:
    def test_response_wrapper_defaults(self) -> None:
        wrapper = ResponseWrapper()
        assert wrapper.success is True
        assert wrapper.data is None
        assert wrapper.errors is None
        assert wrapper.trace_id is None
        assert wrapper.timestamp is None

    def test_response_wrapper_with_data(self) -> None:
        wrapper = ResponseWrapper(data={"id": 1, "name": "test"})
        assert wrapper.data == {"id": 1, "name": "test"}

    def test_response_wrapper_serialization(self) -> None:
        wrapper = ResponseWrapper(success=True, data={"key": "value"})
        dumped = wrapper.model_dump(mode="json")
        assert dumped["success"] is True
        assert dumped["data"] == {"key": "value"}
