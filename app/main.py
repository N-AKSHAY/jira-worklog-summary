from fastapi import FastAPI, HTTPException

from app.models.worklog import WorklogRequest
from app.services.jira_service import get_worklog_summary
from app.ui.router import router as ui_router

app = FastAPI(
    title="Jira Worklog Summary API",
    version="1.0.0"
)


# 🔹 API Endpoint (unchanged)
@app.post("/api/v1/jira-worklogs/summary", tags=["Backend"],
          description="https://stabilixsolutions.atlassian.net/rest/api/3/myself - use this link to get your accountId")
def worklog_summary(request: WorklogRequest):
    """Fetch and summarize Jira work logs for a user within a date range."""
    if request.endDate < request.startDate:
        raise HTTPException(status_code=400, detail="endDate must be greater than or equal to startDate")

    return get_worklog_summary(
        account_id=request.accountId,
        start_date=str(request.startDate),
        end_date=str(request.endDate)
    )


# 🔹 UI Routes
app.include_router(ui_router)

# ✅ Allow running via: python app/main.py
if __name__ == "__main__":
    import uvicorn
    import os

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
        # host="localhost",
        # port=8000,
        # reload=True
    )
