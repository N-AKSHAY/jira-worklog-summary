from pydantic import BaseModel
from datetime import date


class WorklogRequest(BaseModel):
    """Worklog request model"""
    accountId: str
    startDate: date
    endDate: date
