"""Worklog API endpoints."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from app.models.worklog import WorklogRequest
from app.core.dependencies import get_current_user, AuthenticatedUser
from app.core.container import Container
from app.core.error_handler import handle_exceptions
from app.core.exceptions import AuthenticationError, ExternalServiceError, ServiceError
from app.core.session import get_refresh_token, set_access_token, set_refresh_token
from app.core.auth import refresh_access_token
from app.core.logging import get_logger
from app.core.constants import API_TAGS
from app.domain.interfaces import IWorklogService

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/jira-worklogs", tags=[API_TAGS["WORKLOGS"]])


def get_worklog_service(
    user: AuthenticatedUser = Depends(get_current_user)
) -> IWorklogService:
    """Dependency to get worklog service for authenticated user."""
    if isinstance(user, RedirectResponse):
        raise AuthenticationError("Not authenticated")
    return Container.get_worklog_service_for_user(user)


@router.post("/summary", description="Fetch worklog summary for authenticated user")
@handle_exceptions
def get_summary(
    http_request: Request,
    request: WorklogRequest,
    service: IWorklogService = Depends(get_worklog_service),
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Fetch and summarize Jira work logs for a user within a date range."""
    if isinstance(user, RedirectResponse):
        raise AuthenticationError("Not authenticated")

    account_id = request.accountId or user.account_id
    
    try:
        return service.get_worklog_summary(
            account_id=account_id,
            start_date=str(request.startDate),
            end_date=str(request.endDate)
        )
    except (ExternalServiceError, ServiceError) as e:
        if getattr(e, 'status_code', None) == 401:
            refresh_token = get_refresh_token(http_request)
            if not refresh_token:
                raise AuthenticationError("Session expired. Please login again.")
            
            try:
                new_tokens = refresh_access_token(refresh_token)
                set_access_token(http_request, new_tokens["access_token"])
                if "refresh_token" in new_tokens:
                    set_refresh_token(http_request, new_tokens["refresh_token"])
                
                updated_user = AuthenticatedUser(
                    account_id=user.account_id,
                    display_name=user.display_name,
                    email=user.email,
                    access_token=new_tokens["access_token"],
                    cloud_id=user.cloud_id
                )
                
                service = Container.get_worklog_service_for_user(updated_user)
                logger.info("Token refreshed and request retried successfully")
                return service.get_worklog_summary(
                    account_id=account_id,
                    start_date=str(request.startDate),
                    end_date=str(request.endDate)
                )
            except Exception as refresh_error:
                logger.error("Token refresh failed", exc_info=refresh_error)
                raise AuthenticationError("Session expired. Please login again.")
        else:
            raise
