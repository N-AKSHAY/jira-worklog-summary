import secrets
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, ChoiceLoader

from app.core.auth import get_authorization_url, exchange_code_for_tokens, get_user_info
from app.core.session import (
    set_access_token,
    set_refresh_token,
    set_user_info,
    clear_session,
    get_session_data,
    set_session_data
)
from app.core.dependencies import get_current_user, AuthenticatedUser

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[2]

env = Environment(
    loader=ChoiceLoader([
        FileSystemLoader(str(BASE_DIR / "app" / "auth" / "templates")),
        FileSystemLoader(str(BASE_DIR / "app" / "ui" / "templates"))
    ])
)
templates = Jinja2Templates(env=env)


@router.get("/auth/login", tags=["Auth"])
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/auth/authorize", tags=["Auth"])
def authorize(request: Request):
    state = secrets.token_urlsafe(32)
    set_session_data(request, "oauth_state", state)
    auth_url = get_authorization_url(state)
    return RedirectResponse(url=auth_url)


@router.get("/auth/callback", tags=["Auth"])
def callback(request: Request, code: str = None, state: str = None, error: str = None):
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code")
    
    stored_state = get_session_data(request, "oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    try:
        tokens = exchange_code_for_tokens(code)
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        
        if not access_token:
            raise HTTPException(status_code=400, detail="No access token received")
        
        set_access_token(request, access_token)
        if refresh_token:
            set_refresh_token(request, refresh_token)
        
        try:
            user_info = get_user_info(access_token)
            set_user_info(request, user_info)
        except Exception:
            set_session_data(request, "user_info", None)
        
        set_session_data(request, "oauth_state", None)
        return RedirectResponse(url="/ui/worklogs", status_code=302)
    
    except HTTPException:
        clear_session(request)
        raise
    except Exception as e:
        clear_session(request)
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@router.get("/auth/logout", tags=["Auth"])
def logout(request: Request):
    clear_session(request)
    return RedirectResponse(url="/auth/login", status_code=302)


@router.get("/auth/me", tags=["Auth"])
def get_me(user: AuthenticatedUser = Depends(get_current_user)):
    return {
        "accountId": user.account_id,
        "displayName": user.display_name,
        "email": user.email
    }


@router.get("/auth/debug", tags=["Auth"])
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
