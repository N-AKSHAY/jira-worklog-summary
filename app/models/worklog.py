from pydantic import BaseModel
from datetime import date
from typing import Optional


class WorklogRequest(BaseModel):
    """Worklog request model"""
    accountId: Optional[str] = None
    startDate: date
    endDate: date
