"""Worklog business logic service."""

from typing import List, Dict, Any, Optional

from app.domain.interfaces import IWorklogService, IWorklogRepository


class WorklogService(IWorklogService):
    """Service for worklog business logic."""

    def __init__(self, worklog_repository: IWorklogRepository):
        self._repository = worklog_repository
        self._user_account_id: Optional[str] = None

    def get_worklog_summary(
        self,
        account_id: Optional[str] = None,
        start_date: str = "",
        end_date: str = ""
    ) -> List[Dict[str, Any]]:
        account_id = account_id or self._user_account_id
        if not account_id:
            raise ValueError("account_id is required")
        return self._repository.get_worklogs_by_date_range(
            account_id=account_id,
            start_date=start_date,
            end_date=end_date
        )
