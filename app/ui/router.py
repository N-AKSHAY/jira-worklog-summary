from pathlib import Path

from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Union

from app.core.config import TEMPLATE_PATH
from app.core.dependencies import get_current_user, AuthenticatedUser
from app.services.jira_service import get_worklog_summary

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[2]
directory = BASE_DIR / TEMPLATE_PATH

templates = Jinja2Templates(directory=str(directory))


@router.get("/ui/worklogs", tags=["UI"])
def worklog_form(request: Request, user: Union[AuthenticatedUser, RedirectResponse] = Depends(get_current_user)):
    """
    Renders input form
    """
    if isinstance(user, RedirectResponse):
        return user
    
    return templates.TemplateResponse(
        "worklog_summary.html",
        {
            "request": request,
            "data": None,
            "user": {
                "accountId": user.account_id,
                "displayName": user.display_name,
                "email": user.email
            }
        }
    )


@router.post("/ui/worklogs", tags=["UI"])
def render_worklog_summary(
    request: Request,
    startDate: str = Form(...),
    endDate: str = Form(...),
    user: Union[AuthenticatedUser, RedirectResponse] = Depends(get_current_user)
):
    """
    Renders worklog summary UI
    """
    if isinstance(user, RedirectResponse):
        return user
    
    if endDate < startDate:
        raise HTTPException(status_code=400, detail="endDate must be greater than or equal to startDate")

    data = get_worklog_summary(
        account_id=user.account_id,
        start_date=startDate,
        end_date=endDate,
        access_token=user.access_token
    )
    return templates.TemplateResponse(
        "worklog_summary.html",
        {
            "request": request,
            "data": data,
            "accountId": user.account_id,
            "startDate": startDate,
            "endDate": endDate,
            "user": {
                "accountId": user.account_id,
                "displayName": user.display_name,
                "email": user.email
            }
        }
    )
