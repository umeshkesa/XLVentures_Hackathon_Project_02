from __future__ import annotations

import pytest

from adip.data_import.validators import (
    ValidationResult,
    normalize_row,
    validate_date,
    validate_enum,
    validate_field_length,
    validate_integer,
    validate_numeric,
    validate_required_fields,
)


class TestValidators:
    def test_validate_required_fields_pass(self) -> None:
        row = {"id": "1", "name": "test"}
        result = validate_required_fields(row, ["id", "name"])
        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_required_fields_fail(self) -> None:
        row = {"id": "1", "name": ""}
        result = validate_required_fields(row, ["id", "name"])
        assert not result.is_valid
        assert len(result.errors) == 1
        assert result.errors[0].field == "name"

    def test_validate_field_length_pass(self) -> None:
        row = {"name": "short"}
        result = validate_field_length(row, "name", 10)
        assert result.is_valid

    def test_validate_field_length_fail(self) -> None:
        row = {"name": "this is too long"}
        result = validate_field_length(row, "name", 10)
        assert not result.is_valid

    def test_validate_numeric_pass(self) -> None:
        row = {"value": "42.5"}
        result = validate_numeric(row, "value")
        assert result.is_valid

    def test_validate_numeric_fail(self) -> None:
        row = {"value": "not_a_number"}
        result = validate_numeric(row, "value")
        assert not result.is_valid

    def test_validate_integer_pass(self) -> None:
        row = {"value": "42"}
        result = validate_integer(row, "value")
        assert result.is_valid

    def test_validate_integer_fail(self) -> None:
        row = {"value": "42.5"}
        result = validate_integer(row, "value")
        assert not result.is_valid

    def test_validate_enum_pass(self) -> None:
        row = {"severity": "High"}
        result = validate_enum(row, "severity", {"High", "Medium", "Low"})
        assert result.is_valid

    def test_validate_enum_fail(self) -> None:
        row = {"severity": "Invalid"}
        result = validate_enum(row, "severity", {"High", "Medium", "Low"})
        assert not result.is_valid

    def test_validate_date_pass(self) -> None:
        row = {"date": "2026-06-01"}
        result = validate_date(row, "date")
        assert result.is_valid

    def test_validate_date_pass_with_time(self) -> None:
        row = {"date": "2026-06-01 10:15:00"}
        result = validate_date(row, "date")
        assert result.is_valid

    def test_validate_date_fail(self) -> None:
        row = {"date": "01-06-2026"}
        result = validate_date(row, "date")
        assert not result.is_valid

    def test_normalize_row(self) -> None:
        row = {"  id  ": "  1  ", "name": "  test  "}
        result = normalize_row(row)
        assert result["id"] == "1"
        assert result["name"] == "test"

    def test_validation_result_merge(self) -> None:
        r1 = ValidationResult()
        r1.add_error("field1", "error1")
        r2 = ValidationResult()
        r2.add_warning("warning1")
        r1.merge(r2)
        assert len(r1.errors) == 1
        assert len(r1.warnings) == 1

    def test_validation_result_dict(self) -> None:
        result = ValidationResult()
        result.add_error("field1", "error message", row=5)
        d = result.dict()
        assert not d["is_valid"]
        assert d["error_count"] == 1
        assert d["errors"][0]["field"] == "field1"
        assert d["errors"][0]["row"] == 5
