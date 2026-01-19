import sys
from pathlib import Path

# Add project root to Python path when running directly
if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from typing import Union

from app.models.worklog import WorklogRequest
from app.services.jira_service import get_worklog_summary
from app.ui.router import router as ui_router
from app.auth.router import router as auth_router
from app.core.dependencies import get_current_user, AuthenticatedUser
from app.core.config import SECRET_KEY
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(
    title="Jira Worklog Summary API",
    version="1.0.0"
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=86400 * 7, same_site="lax")


# 🔹 Root redirect
@app.get("/", tags=["UI"])
def root():
    """Redirect root path to worklogs UI."""
    return RedirectResponse(url="/ui/worklogs")


# 🔹 API Endpoint
@app.post("/api/v1/jira-worklogs/summary", tags=["Backend"],
          description="Fetch worklog summary for authenticated user")
def worklog_summary(
    request: WorklogRequest,
    user: Union[AuthenticatedUser, RedirectResponse] = Depends(get_current_user)
):
    """Fetch and summarize Jira work logs for a user within a date range."""
    if isinstance(user, RedirectResponse):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    if request.endDate < request.startDate:
        raise HTTPException(status_code=400, detail="endDate must be greater than or equal to startDate")

    account_id = request.accountId or user.account_id

    return get_worklog_summary(
        account_id=account_id,
        start_date=str(request.startDate),
        end_date=str(request.endDate),
        access_token=user.access_token
    )


# 🔹 Auth Routes
app.include_router(auth_router)

# 🔹 UI Routes
app.include_router(ui_router)

# ✅ Allow running via: python app/main.py
if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
        # host="localhost",
        # port=8000,
        # reload=True
    )
