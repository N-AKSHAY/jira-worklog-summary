import secrets
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.core.auth import (
    get_authorization_url,
    exchange_code_for_tokens,
    get_user_info
)
from app.core.session import (
    set_access_token,
    set_refresh_token,
    set_user_info,
    clear_session
)
from app.core.dependencies import get_current_user, AuthenticatedUser

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[2]
# Include both auth and ui template directories
from jinja2 import Environment, FileSystemLoader, ChoiceLoader
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
def login(request: Request):
    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state
    
    auth_url = get_authorization_url(state)
    return RedirectResponse(url=auth_url)


@router.get("/auth/callback", tags=["Auth"])
def callback(request: Request, code: str = None, state: str = None, error: str = None):
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"OAuth error: {error}"
        )
    
    if not code:
        raise HTTPException(
            status_code=400,
            detail="Missing authorization code"
        )
    
    stored_state = request.session.get("oauth_state")
    if not stored_state or stored_state != state:
        raise HTTPException(
            status_code=400,
            detail="Invalid state parameter"
        )
    
    try:
        tokens = exchange_code_for_tokens(code)
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        
        if not access_token:
            raise HTTPException(
                status_code=400,
                detail="No access token received"
            )
        
        user_info = get_user_info(access_token)
        
        set_access_token(request, access_token)
        if refresh_token:
            set_refresh_token(request, refresh_token)
        set_user_info(request, user_info)
        
        request.session.pop("oauth_state", None)
        
        return RedirectResponse(url="/ui/worklogs", status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )


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
