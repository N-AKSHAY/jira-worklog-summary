from authlib.integrations.requests_client import OAuth2Session
from fastapi import HTTPException
import requests

from app.core.config import (
    JIRA_OAUTH_CLIENT_ID,
    JIRA_OAUTH_CLIENT_SECRET,
    JIRA_OAUTH_REDIRECT_URI,
    JIRA_OAUTH_AUTHORIZE_URL,
    JIRA_OAUTH_TOKEN_URL,
    JIRA_DOMAIN
)


def get_oauth_client(state: str = None):
    return OAuth2Session(
        client_id=JIRA_OAUTH_CLIENT_ID,
        client_secret=JIRA_OAUTH_CLIENT_SECRET,
        redirect_uri=JIRA_OAUTH_REDIRECT_URI,
        scope="read:jira-work read:jira-user"
    )


def get_authorization_url(state: str) -> str:
    client = get_oauth_client(state)
    auth_url, _ = client.create_authorization_url(
        JIRA_OAUTH_AUTHORIZE_URL,
        state=state
    )
    return auth_url


def exchange_code_for_tokens(code: str) -> dict:
    client = get_oauth_client()
    try:
        token = client.fetch_token(
            JIRA_OAUTH_TOKEN_URL,
            code=code,
            client_id=JIRA_OAUTH_CLIENT_ID,
            client_secret=JIRA_OAUTH_CLIENT_SECRET
        )
        return token
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange authorization code for tokens: {str(e)}"
        )


def refresh_access_token(refresh_token: str) -> dict:
    client = get_oauth_client()
    try:
        token = client.refresh_token(
            JIRA_OAUTH_TOKEN_URL,
            refresh_token=refresh_token,
            client_id=JIRA_OAUTH_CLIENT_ID,
            client_secret=JIRA_OAUTH_CLIENT_SECRET
        )
        return token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to refresh access token: {str(e)}"
        )


def get_user_info(access_token: str) -> dict:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(
            f"https://{JIRA_DOMAIN}/rest/api/3/myself",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Failed to fetch user info: {str(e)}"
        )


def get_authenticated_session(access_token: str):
    return OAuth2Session(
        client_id=JIRA_OAUTH_CLIENT_ID,
        client_secret=JIRA_OAUTH_CLIENT_SECRET,
        token={"access_token": access_token, "token_type": "Bearer"}
    )
