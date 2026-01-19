"""UI routes and templates."""

from pathlib import Path
from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Union

from app.core.config import TEMPLATE_PATH
from app.core.dependencies import get_current_user, AuthenticatedUser
from app.core.session import get_user_info
from app.core.container import Container
from app.domain.interfaces import IWorklogService

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[2]
directory = BASE_DIR / TEMPLATE_PATH
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
        raise HTTPException(status_code=401, detail="Not authenticated")
    return Container.get_worklog_service_for_user(user)


@router.get("/ui/worklogs", tags=["UI"])
def worklog_form(
    request: Request,
    user: Union[AuthenticatedUser, RedirectResponse] = Depends(get_current_user)
):
    if isinstance(user, RedirectResponse):
        return user
    
    return templates.TemplateResponse(
        "worklog_summary.html",
        {
            "request": request,
            "data": None,
            "user": _build_user_context(user, request)
        }
    )


@router.post("/ui/worklogs", tags=["UI"])
def render_worklog_summary(
    request: Request,
    startDate: str = Form(...),
    endDate: str = Form(...),
    user: Union[AuthenticatedUser, RedirectResponse] = Depends(get_current_user),
    service: IWorklogService = Depends(get_worklog_service)
):
    if isinstance(user, RedirectResponse):
        return user
    
    if endDate < startDate:
        raise HTTPException(
            status_code=400,
            detail="endDate must be greater than or equal to startDate"
        )

    data = service.get_worklog_summary(
        account_id=user.account_id,
        start_date=startDate,
        end_date=endDate
    )
    
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
