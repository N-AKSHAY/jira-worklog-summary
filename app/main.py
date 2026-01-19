import sys
from pathlib import Path

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from app.api.v1.worklogs import router as worklogs_router
from app.ui.router import router as ui_router
from app.auth.router import router as auth_router
from app.core.session import apply_session_cookies

app = FastAPI(title="Jira Worklog Summary API", version="1.0.0")


class SessionCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if isinstance(response, StarletteResponse):
            apply_session_cookies(response, request)
        return response


app.add_middleware(SessionCookieMiddleware)


@app.get("/", tags=["UI"])
def root():
    return RedirectResponse(url="/ui/worklogs")


app.include_router(worklogs_router)
app.include_router(auth_router)
app.include_router(ui_router)


if __name__ == "__main__":
    import os
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )
