from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates

from app.core.config import TEMPLATE_PATH
from app.services.jira_service import get_worklog_summary

router = APIRouter()
templates = Jinja2Templates(directory=TEMPLATE_PATH)


@router.get("/ui/worklogs", tags=["UI"])
def worklog_form(request: Request):
    """
    Renders input form
    """
    return templates.TemplateResponse("worklog_summary.html", {"request": request, "data": None})


@router.post("/ui/worklogs", tags=["UI"])
def render_worklog_summary(request: Request, accountId: str = Form(...), startDate: str = Form(...),
                           endDate: str = Form(...)):
    """
    Renders worklog summary UI
    """
    if endDate < startDate:
        raise HTTPException(status_code=400, detail="endDate must be greater than or equal to startDate")

    data = get_worklog_summary(account_id=accountId, start_date=startDate, end_date=endDate)
    return templates.TemplateResponse("worklog_summary.html",
                                      {
                                          "request": request,
                                          "data": data,
                                          "accountId": accountId,
                                          "startDate": startDate,
                                          "endDate": endDate
                                      })
