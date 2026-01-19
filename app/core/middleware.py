"""Application middleware."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from app.core.session import apply_session_cookies


class SessionCookieMiddleware(BaseHTTPMiddleware):
    """Middleware to apply session cookies to responses."""
    
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if isinstance(response, StarletteResponse):
            apply_session_cookies(response, request)
        return response
