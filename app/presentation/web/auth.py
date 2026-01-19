"""Authentication routes."""

import secrets
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.core.auth import get_authorization_url, exchange_code_for_tokens, get_user_info
from app.core.exceptions import ValidationError, AuthenticationError, ExternalServiceError
from app.core.logging import get_logger
from app.core.session import (
    set_access_token,
    set_refresh_token,
    set_user_info,
    clear_session,
    get_session_data,
    set_session_data
)
from app.core.dependencies import get_current_user, AuthenticatedUser
from app.core.constants import API_TAGS, ROUTES

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[3]
logger = get_logger(__name__)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get(ROUTES["AUTH_LOGIN"], tags=[API_TAGS["AUTH"]])
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get(ROUTES["AUTH_AUTHORIZE"], tags=[API_TAGS["AUTH"]])
def authorize(request: Request):
    state = secrets.token_urlsafe(32)
    set_session_data(request, "oauth_state", state)
    auth_url = get_authorization_url(state)
    return RedirectResponse(url=auth_url)


@router.get(ROUTES["AUTH_CALLBACK"], tags=[API_TAGS["AUTH"]])
def callback(request: Request, code: str = None, state: str = None, error: str = None):
    if error:
        logger.warning("OAuth callback error", extra={"error": error})
        if error == "access_denied":
            clear_session(request)
            return RedirectResponse(url=ROUTES["AUTH_DENIED"], status_code=302)
        raise ValidationError(f"OAuth error: {error}")
    
    if not code:
        raise ValidationError("Missing authorization code")
    
    stored_state = get_session_data(request, "oauth_state")
    if not stored_state or stored_state != state:
        logger.warning("Invalid OAuth state", extra={"stored_state": stored_state, "received_state": state})
        raise ValidationError("Invalid state parameter")
    
    try:
        tokens = exchange_code_for_tokens(code)
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        
        if not access_token:
            raise ValidationError("No access token received")
        
        set_access_token(request, access_token)
        if refresh_token:
            set_refresh_token(request, refresh_token)
        
        try:
            user_info = get_user_info(access_token)
            set_user_info(request, user_info)
        except Exception as e:
            logger.warning("Failed to fetch user info", exc_info=e)
            set_session_data(request, "user_info", None)
        
        set_session_data(request, "oauth_state", None)
        return RedirectResponse(url=ROUTES["UI_WORKLOGS"], status_code=302)
    
    except (ValidationError, AuthenticationError, ExternalServiceError):
        clear_session(request)
        raise
    except Exception as e:
        logger.error("Authentication failed", exc_info=e)
        clear_session(request)
        raise AuthenticationError(f"Authentication failed: {str(e)}")


@router.get(ROUTES["AUTH_LOGOUT"], tags=[API_TAGS["AUTH"]])
def logout(request: Request):
    clear_session(request)
    return RedirectResponse(url=ROUTES["AUTH_LOGIN"], status_code=302)


@router.get(ROUTES["AUTH_DENIED"], tags=[API_TAGS["AUTH"]])
def denied(request: Request):
    return templates.TemplateResponse("auth_denied.html", {"request": request})


@router.get(ROUTES["AUTH_ME"], tags=[API_TAGS["AUTH"]])
def get_me(user: AuthenticatedUser = Depends(get_current_user)):
    return {
        "accountId": user.account_id,
        "displayName": user.display_name,
        "email": user.email
    }


@router.get("/auth/debug", tags=[API_TAGS["AUTH"]])
def debug_session(request: Request):
    access_token = get_session_data(request, "access_token")
    refresh_token = get_session_data(request, "refresh_token")
    user_info = get_session_data(request, "user_info")
    
    return {
        "cookies_received": list(request.cookies.keys()),
        "has_access_token": access_token is not None,
        "has_refresh_token": refresh_token is not None,
        "has_user_info": user_info is not None,
        "access_token": (access_token[:20] + "...") if access_token else "NOT SET",
        "user_info": user_info if user_info else "NOT SET"
    }
