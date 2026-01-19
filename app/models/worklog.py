"""Data models for worklog requests and responses."""

from pydantic import BaseModel, Field, field_validator
from datetime import date
from typing import Optional

from app.core.validators import validate_date_range


class WorklogRequest(BaseModel):
    """Request model for worklog summary.
    
    Attributes:
        accountId: Optional Jira account ID. If not provided, uses authenticated user's ID.
        startDate: Start date for worklog query (inclusive).
        endDate: End date for worklog query (inclusive).
    """
    
    accountId: Optional[str] = Field(
        default=None,
        description="Jira account ID. If not provided, uses authenticated user's ID."
    )
    startDate: date = Field(
        description="Start date for worklog query (inclusive)"
    )
    endDate: date = Field(
        description="End date for worklog query (inclusive)"
    )
    
    @field_validator("endDate")
    @classmethod
    def validate_date_range(cls, v, info):
        """Validate that endDate is after or equal to startDate."""
        if "startDate" in info.data:
            validate_date_range(str(info.data["startDate"]), str(v))
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "accountId": "557058:abc123",
                "startDate": "2026-01-01",
                "endDate": "2026-01-31"
            }
        }
