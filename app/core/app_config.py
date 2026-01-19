"""Application configuration and setup."""

from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.templating import Jinja2Templates

from app.core.error_handler import global_exception_handler
from app.core.exceptions import BaseApplicationException
from app.core.middleware import SessionCookieMiddleware
from app.core.constants import ROUTES


async def not_found_handler(request: Request, exc: StarletteHTTPException):
    """Handle 404 Not Found errors with appropriate response format."""
    if exc.status_code != 404:
        return await global_exception_handler(request, exc)
    
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={
                "error": "NOT_FOUND",
                "message": "Resource not found",
                "details": {"path": request.url.path}
            }
        )
    
    templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent.parent / "templates"))
    return templates.TemplateResponse(
        "404.html",
        {"request": request, "path": request.url.path},
        status_code=404
    )


def configure_exception_handlers(app: FastAPI) -> None:
    """Configure global exception handlers."""
    app.add_exception_handler(StarletteHTTPException, not_found_handler)
    app.add_exception_handler(BaseApplicationException, global_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)


def configure_middleware(app: FastAPI) -> None:
    """Configure application middleware."""
    app.add_middleware(SessionCookieMiddleware)


def configure_static_files(app: FastAPI, base_dir: Path) -> None:
    """Configure static file serving."""
    static_dir = base_dir / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


def configure_routes(app: FastAPI) -> None:
    """Configure application routes."""
    from app.presentation.api.v1.worklogs import router as worklogs_router
    from app.presentation.web.worklogs import router as ui_router
    from app.presentation.web.auth import router as auth_router
    
    @app.get(ROUTES["ROOT"], tags=["UI"])
    def root():
        return RedirectResponse(url=ROUTES["UI_WORKLOGS"])
    
    app.include_router(worklogs_router)
    app.include_router(auth_router)
    app.include_router(ui_router)


def create_app(environment: Optional[str] = None) -> FastAPI:
    """Create and configure FastAPI application.
    
    Args:
        environment: Optional environment name (development, production, etc.)
    """
    app = FastAPI(
        title="Jira Worklog Summary API",
        version="1.0.0",
        docs_url="/docs" if environment != "production" else None,
        redoc_url="/redoc" if environment != "production" else None
    )
    
    base_dir = Path(__file__).resolve().parent.parent.parent
    
    configure_exception_handlers(app)
    configure_middleware(app)
    configure_static_files(app, base_dir)
    configure_routes(app)
    
    return app
