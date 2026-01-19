from fastapi import Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Optional, Union

from app.core.session import (
    get_access_token,
    get_user_info,
    get_refresh_token
)
from app.core.auth import (
    refresh_access_token,
    get_user_info as fetch_user_info,
    get_authenticated_session
)
from app.core.config import JIRA_EMAIL, JIRA_API_TOKEN


class AuthenticatedUser:
    def __init__(self, account_id: str, display_name: str, email: str, access_token: str):
        self.account_id = account_id
        self.display_name = display_name
        self.email = email
        self.access_token = access_token


def get_current_user(request: Request) -> Union[AuthenticatedUser, RedirectResponse]:
    access_token = get_access_token(request)
    
    if not access_token:
        if request.url.path.startswith("/ui/"):
            return RedirectResponse(url="/auth/login", status_code=302)
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )
    
    user_info = get_user_info(request)
    
    if not user_info:
        try:
            user_info = fetch_user_info(access_token)
            request.session["user_info"] = user_info
        except HTTPException:
            refresh_token = get_refresh_token(request)
            if refresh_token:
                try:
                    new_tokens = refresh_access_token(refresh_token)
                    request.session["access_token"] = new_tokens["access_token"]
                    if "refresh_token" in new_tokens:
                        request.session["refresh_token"] = new_tokens["refresh_token"]
                    user_info = fetch_user_info(new_tokens["access_token"])
                    request.session["user_info"] = user_info
                except HTTPException:
                    raise HTTPException(
                        status_code=401,
                        detail="Session expired. Please login again."
                    )
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Session expired. Please login again."
                )
    
    return AuthenticatedUser(
        account_id=user_info.get("accountId"),
        display_name=user_info.get("displayName", ""),
        email=user_info.get("emailAddress", ""),
        access_token=access_token
    )


def require_auth(request: Request, user: AuthenticatedUser = Depends(get_current_user)):
    return user


def get_fallback_auth():
    if JIRA_EMAIL and JIRA_API_TOKEN:
        from requests.auth import HTTPBasicAuth
        return HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
    return None
