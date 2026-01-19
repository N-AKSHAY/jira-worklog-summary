"""Worklog API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse

from app.models.worklog import WorklogRequest
from app.core.dependencies import get_current_user, AuthenticatedUser
from app.core.container import Container
from app.domain.interfaces import IWorklogService

router = APIRouter(prefix="/api/v1/jira-worklogs", tags=["Worklogs"])


def get_worklog_service(
    user: AuthenticatedUser = Depends(get_current_user)
) -> IWorklogService:
    """Dependency to get worklog service for authenticated user."""
    if isinstance(user, RedirectResponse):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return Container.get_worklog_service_for_user(user)


@router.post("/summary", description="Fetch worklog summary for authenticated user")
def get_summary(
    request: WorklogRequest,
    service: IWorklogService = Depends(get_worklog_service),
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Fetch and summarize Jira work logs for a user within a date range."""
    if isinstance(user, RedirectResponse):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if request.endDate < request.startDate:
        raise HTTPException(
            status_code=400,
            detail="endDate must be greater than or equal to startDate"
        )

    account_id = request.accountId or user.account_id
    
    return service.get_worklog_summary(
        account_id=account_id,
        start_date=str(request.startDate),
        end_date=str(request.endDate)
    )
