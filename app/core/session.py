from typing import Optional
from fastapi import Request, Response
import json
import base64

SESSION_ID_COOKIE = "session_id"
ACCESS_TOKEN_COOKIE = "access_token"
REFRESH_TOKEN_COOKIE = "refresh_token"
USER_INFO_COOKIE = "user_info"
SESSION_MAX_AGE = 86400 * 7


def _encode_cookie_value(value: str) -> str:
    return base64.b64encode(value.encode('utf-8')).decode('utf-8')


def _decode_cookie_value(value: str) -> str:
    try:
        return base64.b64decode(value.encode('utf-8')).decode('utf-8')
    except Exception:
        return ""


def get_session_data(request: Request, key: str = None):
    if key == "access_token":
        return request.cookies.get(ACCESS_TOKEN_COOKIE)
    elif key == "refresh_token":
        return request.cookies.get(REFRESH_TOKEN_COOKIE)
    elif key == "user_info":
        user_info_str = request.cookies.get(USER_INFO_COOKIE)
        if user_info_str:
            try:
                decoded = _decode_cookie_value(user_info_str)
                return json.loads(decoded)
            except Exception:
                return None
        return None
    elif key == "oauth_state":
        return request.cookies.get("oauth_state")
    elif key is None:
        return {
            "access_token": request.cookies.get(ACCESS_TOKEN_COOKIE),
            "refresh_token": request.cookies.get(REFRESH_TOKEN_COOKIE),
            "user_info": get_session_data(request, "user_info"),
            "oauth_state": request.cookies.get("oauth_state")
        }
    return None


def set_session_data(request: Request, key: str, value):
    if not hasattr(request.state, 'session_cookies'):
        request.state.session_cookies = {}
    
    if key == "access_token":
        request.state.session_cookies[ACCESS_TOKEN_COOKIE] = value
    elif key == "refresh_token":
        request.state.session_cookies[REFRESH_TOKEN_COOKIE] = value
    elif key == "user_info":
        user_info_json = json.dumps(value)
        encoded = _encode_cookie_value(user_info_json)
        request.state.session_cookies[USER_INFO_COOKIE] = encoded
    elif key == "oauth_state":
        request.state.session_cookies["oauth_state"] = value
    else:
        request.state.session_cookies[key] = value


def clear_session(request: Request):
    if hasattr(request.state, 'session_cookies'):
        request.state.session_cookies = {}
    if not hasattr(request.state, 'cookies_to_delete'):
        request.state.cookies_to_delete = []
    request.state.cookies_to_delete.extend([
        SESSION_ID_COOKIE,
        ACCESS_TOKEN_COOKIE,
        REFRESH_TOKEN_COOKIE,
        USER_INFO_COOKIE,
        "oauth_state"
    ])


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
    avatar_urls = user_info.get("avatarUrls", {})
    essential_info = {
        "accountId": user_info.get("accountId"),
        "displayName": user_info.get("displayName"),
        "emailAddress": user_info.get("emailAddress"),
        "cloudId": user_info.get("cloudId"),
        "accountType": user_info.get("accountType"),
        "timeZone": user_info.get("timeZone"),
        "locale": user_info.get("locale"),
        "avatarUrl": avatar_urls.get("48x48") or avatar_urls.get("32x32") or avatar_urls.get("24x24") or ""
    }
    set_session_data(request, "user_info", essential_info)


def apply_session_cookies(response: Response, request: Request):
    """Apply session cookies to response and cleanup request state."""
    if hasattr(request.state, 'cookies_to_delete'):
        for cookie_name in request.state.cookies_to_delete:
            response.delete_cookie(cookie_name, path="/")
        delattr(request.state, 'cookies_to_delete')
    
    if hasattr(request.state, 'session_cookies'):
        for cookie_name, cookie_value in request.state.session_cookies.items():
            if cookie_value is None:
                response.delete_cookie(cookie_name, path="/")
            else:
                response.set_cookie(
                    cookie_name,
                    cookie_value,
                    max_age=SESSION_MAX_AGE,
                    httponly=True,
                    samesite="lax",
                    secure=False,
                    path="/"
                )
        delattr(request.state, 'session_cookies')
