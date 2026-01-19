"""Worklog UI routes."""

from pathlib import Path
from datetime import date, timedelta
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Union, Optional

from app.core.dependencies import get_current_user, AuthenticatedUser
from app.core.session import (
    get_user_info,
    get_refresh_token,
    set_access_token,
    set_refresh_token
)
from app.core.auth import refresh_access_token
from app.core.container import Container
from app.core.exceptions import AuthenticationError, ExternalServiceError, ServiceError
from app.core.validators import validate_date_range
from app.core.constants import API_TAGS, ROUTES
from app.core.logging import get_logger
from app.domain.interfaces import IWorklogService

logger = get_logger(__name__)

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[3]
directory = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(directory))


def _build_user_context(user: AuthenticatedUser, request: Request) -> dict:
    user_info = get_user_info(request) or {}
    return {
        "accountId": user.account_id,
        "displayName": user.display_name,
        "email": user.email,
        "avatarUrl": user_info.get("avatarUrl", ""),
        "accountType": user_info.get("accountType", ""),
        "timeZone": user_info.get("timeZone", ""),
        "locale": user_info.get("locale", "")
    }


def get_worklog_service(
    user: AuthenticatedUser = Depends(get_current_user)
) -> IWorklogService:
    """Dependency to get worklog service for authenticated user."""
    if isinstance(user, RedirectResponse):
        raise AuthenticationError("Not authenticated")
    return Container.get_worklog_service_for_user(user)


def _get_current_week_dates():
    """Calculate current week start (Monday) and end (Sunday) dates."""
    today = date.today()
    day_of_week = today.weekday()
    start_of_week = today - timedelta(days=day_of_week)
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week.isoformat(), end_of_week.isoformat()


@router.get(ROUTES["UI_WORKLOGS"], tags=[API_TAGS["UI"]])
def worklog_form(
    request: Request,
    user: Union[AuthenticatedUser, RedirectResponse] = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    
    start_date, end_date = _get_current_week_dates()
    data = None
    
    service = Container.get_worklog_service_for_user(user)
    
    try:
        data = service.get_worklog_summary(
            account_id=user.account_id,
            start_date=start_date,
            end_date=end_date
        )
    except (ExternalServiceError, ServiceError) as e:
        if getattr(e, 'status_code', None) == 401:
            refresh_token = get_refresh_token(request)
            if refresh_token:
                try:
                    new_tokens = refresh_access_token(refresh_token)
                    set_access_token(request, new_tokens["access_token"])
                    if "refresh_token" in new_tokens:
                        set_refresh_token(request, new_tokens["refresh_token"])
                    
                    updated_user = AuthenticatedUser(
                        account_id=user.account_id,
                        display_name=user.display_name,
                        email=user.email,
                        access_token=new_tokens["access_token"],
                        cloud_id=user.cloud_id
                    )
                    
                    service = Container.get_worklog_service_for_user(updated_user)
                    data = service.get_worklog_summary(
                        account_id=user.account_id,
                        start_date=start_date,
                        end_date=end_date
                    )
                    logger.info("Token refreshed and current week data loaded")
                except Exception as refresh_error:
                    logger.error("Token refresh failed on page load", exc_info=refresh_error)
        else:
            logger.warning("Failed to load current week worklogs on page load", exc_info=e)
    
    return templates.TemplateResponse(
        "worklog_summary.html",
        {
            "request": request,
            "data": data,
            "startDate": start_date,
            "endDate": end_date,
            "user": _build_user_context(user, request)
        }
    )


@router.post(ROUTES["UI_WORKLOGS"], tags=[API_TAGS["UI"]])
def render_worklog_summary(
    request: Request,
    startDate: str = Form(...),
    endDate: str = Form(...),
    user: Union[AuthenticatedUser, RedirectResponse] = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    
    validate_date_range(startDate, endDate)

    service = Container.get_worklog_service_for_user(user)
    
    try:
        data = service.get_worklog_summary(
            account_id=user.account_id,
            start_date=startDate,
            end_date=endDate
        )
    except (ExternalServiceError, ServiceError) as e:
        if getattr(e, 'status_code', None) == 401:
            refresh_token = get_refresh_token(request)
            if not refresh_token:
                raise AuthenticationError("Session expired. Please login again.")
            
            try:
                new_tokens = refresh_access_token(refresh_token)
                set_access_token(request, new_tokens["access_token"])
                if "refresh_token" in new_tokens:
                    set_refresh_token(request, new_tokens["refresh_token"])
                
                updated_user = AuthenticatedUser(
                    account_id=user.account_id,
                    display_name=user.display_name,
                    email=user.email,
                    access_token=new_tokens["access_token"],
                    cloud_id=user.cloud_id
                )
                
                service = Container.get_worklog_service_for_user(updated_user)
                data = service.get_worklog_summary(
                    account_id=user.account_id,
                    start_date=startDate,
                    end_date=endDate
                )
                logger.info("Token refreshed and request retried successfully")
            except Exception as refresh_error:
                logger.error("Token refresh failed", exc_info=refresh_error)
                raise AuthenticationError("Session expired. Please login again.")
        else:
            raise
    
    return templates.TemplateResponse(
        "worklog_summary.html",
        {
            "request": request,
            "data": data,
            "accountId": user.account_id,
            "startDate": startDate,
            "endDate": endDate,
            "user": _build_user_context(user, request)
        }
    )
