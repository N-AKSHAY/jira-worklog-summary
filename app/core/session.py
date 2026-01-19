from typing import Optional
from fastapi import Request

from app.core.config import SECRET_KEY

SESSION_COOKIE_NAME = "session"
SESSION_MAX_AGE = 86400 * 7


def get_session_middleware():
    from starlette.middleware.sessions import SessionMiddleware
    return SessionMiddleware(
        secret_key=SECRET_KEY,
        max_age=SESSION_MAX_AGE,
        same_site="lax"
    )


def get_session_data(request: Request, key: str = None):
    session = request.session
    if key:
        return session.get(key)
    return session


def set_session_data(request: Request, key: str, value):
    request.session[key] = value


def clear_session(request: Request):
    request.session.clear()


def get_access_token(request: Request) -> Optional[str]:
    return get_session_data(request, "access_token")


def set_access_token(request: Request, token: str):
    set_session_data(request, "access_token", token)


def get_refresh_token(request: Request) -> Optional[str]:
    return get_session_data(request, "refresh_token")


def set_refresh_token(request: Request, token: str):
    set_session_data(request, "refresh_token", token)


def get_user_info(request: Request) -> Optional[dict]:
    return get_session_data(request, "user_info")


def set_user_info(request: Request, user_info: dict):
    set_session_data(request, "user_info", user_info)
