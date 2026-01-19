"""Validation utilities."""

from typing import Any, Optional
from datetime import datetime
from app.core.exceptions import ValidationError


def validate_date_range(start_date: str, end_date: str) -> None:
    """Validate that start_date is before or equal to end_date."""
    if start_date > end_date:
        raise ValidationError(
            message="start_date must be less than or equal to end_date",
            details={"start_date": start_date, "end_date": end_date}
        )


def validate_date_format(date_str: str, field_name: str = "date") -> None:
    """Validate date string format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(
            message=f"{field_name} must be in YYYY-MM-DD format",
            details={"field": field_name, "value": date_str}
        )


def validate_required(value: Any, field_name: str) -> None:
    """Validate that a required field is not empty."""
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError(
            message=f"{field_name} is required",
            details={"field": field_name}
        )


def validate_not_empty(value: Any, field_name: str) -> None:
    """Validate that a value is not empty."""
    if not value:
        raise ValidationError(
            message=f"{field_name} cannot be empty",
            details={"field": field_name}
        )
