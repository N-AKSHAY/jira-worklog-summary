"""Error handling utilities and decorators."""

from functools import wraps
from typing import Callable, Any
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import BaseApplicationException
from app.core.logging import get_logger

logger = get_logger(__name__)


def handle_exceptions(func: Callable) -> Callable:
    """Decorator to handle exceptions and convert to HTTP responses."""
    
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            if hasattr(func, '__wrapped__'):
                return await func(*args, **kwargs)
            result = func(*args, **kwargs)
            if hasattr(result, '__await__'):
                return await result
            return result
        except BaseApplicationException as e:
            logger.error(
                f"Application error in {func.__name__}",
                extra={
                    "error_code": e.error_code,
                    "status_code": e.status_code,
                    "details": e.details
                }
            )
            raise HTTPException(
                status_code=e.status_code,
                detail={
                    "error": e.error_code,
                    "message": e.message,
                    "details": e.details
                }
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error in {func.__name__}",
                exc_info=e
            )
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred"
                }
            )
    
    return wrapper


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for FastAPI."""
    
    if isinstance(exc, BaseApplicationException):
        logger.error(
            "Application exception",
            extra={
                "error_code": exc.error_code,
                "status_code": exc.status_code,
                "path": str(request.url.path),
                "details": exc.details
            }
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details
            }
        )
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP_ERROR",
                "message": exc.detail if isinstance(exc.detail, str) else exc.detail.get("message", "Error"),
                "details": exc.detail if isinstance(exc.detail, dict) else {}
            }
        )
    
    logger.error(
        "Unhandled exception",
        extra={"path": str(request.url.path)},
        exc_info=exc
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred"
        }
    )
