"""Worklog business logic service."""

from typing import List, Dict, Any, Optional

from app.domain.interfaces import IWorklogService, IWorklogRepository
from app.core.base import BaseService
from app.core.exceptions import ExternalServiceError
from app.core.validators import validate_date_range, validate_required


class WorklogService(BaseService, IWorklogService):
    """Service for worklog business logic."""

    def __init__(self, worklog_repository: IWorklogRepository, user_account_id: Optional[str] = None):
        super().__init__()
        self._repository = worklog_repository
        self._user_account_id = user_account_id

    def get_worklog_summary(
        self,
        account_id: Optional[str] = None,
        start_date: str = "",
        end_date: str = ""
    ) -> List[Dict[str, Any]]:
        account_id = account_id or self._user_account_id
        validate_required(account_id, "account_id")
        validate_required(start_date, "start_date")
        validate_required(end_date, "end_date")
        validate_date_range(start_date, end_date)
        
        try:
            return self._repository.get_worklogs_by_date_range(
                account_id=account_id,
                start_date=start_date,
                end_date=end_date
            )
        except ExternalServiceError:
            raise
        except Exception as e:
            self._handle_error(
                error=e,
                operation="get_worklog_summary",
                context={
                    "account_id": account_id,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
