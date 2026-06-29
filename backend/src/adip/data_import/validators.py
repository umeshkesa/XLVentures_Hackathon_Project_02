from __future__ import annotations

from typing import Any

import structlog

log = structlog.get_logger(__name__)


class ValidationError(Exception):
    def __init__(self, field: str, message: str, row: int = 0) -> None:
        self.field = field
        self.message = message
        self.row = row
        super().__init__(f"Row {row}: {field} - {message}")


class ValidationResult:
    def __init__(self) -> None:
        self.errors: list[ValidationError] = []
        self.warnings: list[str] = []

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, field: str, message: str, row: int = 0) -> None:
        err = ValidationError(field, message, row)
        self.errors.append(err)
        log.warning("validation.error", field=field, message=message, row=row)

    def add_warning(self, message: str) -> None:
        self.warnings.append(message)
        log.warning("validation.warning", message=message)

    def merge(self, other: ValidationResult) -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)

    def dict(self) -> dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": [
                {"row": e.row, "field": e.field, "message": e.message} for e in self.errors
            ],
            "warnings": self.warnings,
        }


def validate_required_fields(row: dict[str, str], required: list[str], row_num: int = 0) -> ValidationResult:
    """Check that all required fields are present and non-empty."""
    result = ValidationResult()
    for field in required:
        val = row.get(field, "")
        if not val or val.strip() == "":
            result.add_error(field, f"Missing required field: {field}", row_num)
    return result


def validate_field_length(
    row: dict[str, str], field: str, max_len: int, row_num: int = 0
) -> ValidationResult:
    """Check that a field does not exceed max length."""
    result = ValidationResult()
    val = row.get(field, "")
    if len(val) > max_len:
        result.add_error(field, f"Field exceeds max length {max_len}: {len(val)}", row_num)
    return result


def validate_numeric(
    row: dict[str, str], field: str, row_num: int = 0, allow_empty: bool = True
) -> ValidationResult:
    """Check that a field contains a valid number."""
    result = ValidationResult()
    val = row.get(field, "")
    if not val and allow_empty:
        return result
    try:
        float(val)
    except (ValueError, TypeError):
        result.add_error(field, f"Field is not a valid number: {val}", row_num)
    return result


def validate_integer(
    row: dict[str, str], field: str, row_num: int = 0, allow_empty: bool = True
) -> ValidationResult:
    """Check that a field contains a valid integer."""
    result = ValidationResult()
    val = row.get(field, "")
    if not val and allow_empty:
        return result
    try:
        int(val)
    except (ValueError, TypeError):
        result.add_error(field, f"Field is not a valid integer: {val}", row_num)
    return result


def validate_enum(
    row: dict[str, str], field: str, allowed: set[str], row_num: int = 0, allow_empty: bool = True
) -> ValidationResult:
    """Check that a field value is one of the allowed values."""
    result = ValidationResult()
    val = row.get(field, "")
    if not val and allow_empty:
        return result
    if val not in allowed:
        result.add_error(field, f"Invalid value '{val}'. Allowed: {sorted(allowed)}", row_num)
    return result


def validate_date(
    row: dict[str, str], field: str, row_num: int = 0, allow_empty: bool = True
) -> ValidationResult:
    """Strict date format validation (expects YYYY-MM-DD or YYYY-MM-DD HH:MM:SS)."""
    result = ValidationResult()
    val = row.get(field, "")
    if not val and allow_empty:
        return result
    date_part = val.split(" ")[0]
    parts = date_part.split("-")
    if len(parts) != 3:
        result.add_error(field, f"Invalid date format: {val} (expected YYYY-MM-DD)", row_num)
        return result
    year, month, day = parts
    if not (year.isdigit() and month.isdigit() and day.isdigit()):
        result.add_error(field, f"Invalid non-numeric date: {val}", row_num)
    elif not (len(year) == 4 and len(month) == 2 and len(day) == 2):
        result.add_error(field, f"Invalid date segment lengths: {val} (expected YYYY-MM-DD)", row_num)
    return result


def normalize_row(row: dict[str, str]) -> dict[str, str]:
    """Strip whitespace from all values in a row and remove BOM."""
    return {k.strip(): v.strip() for k, v in row.items()}
