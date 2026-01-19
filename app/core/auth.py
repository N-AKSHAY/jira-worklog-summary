import requests
from fastapi import HTTPException
from urllib.parse import urlencode
import logging

from app.core.config import (
    JIRA_OAUTH_CLIENT_ID,
    JIRA_OAUTH_CLIENT_SECRET,
    JIRA_OAUTH_REDIRECT_URI,
    JIRA_OAUTH_AUTHORIZE_URL,
    JIRA_OAUTH_TOKEN_URL,
    JIRA_API_BASE_URL,
    JIRA_DOMAIN
)

logger = logging.getLogger(__name__)
OAUTH_SCOPES = "read:jira-work read:jira-user offline_access"


def get_authorization_url(state: str) -> str:
    params = {
        "audience": "api.atlassian.com",
        "client_id": JIRA_OAUTH_CLIENT_ID,
        "scope": OAUTH_SCOPES,
        "redirect_uri": JIRA_OAUTH_REDIRECT_URI,
        "state": state,
        "response_type": "code",
        "prompt": "consent"
    }
    return f"{JIRA_OAUTH_AUTHORIZE_URL}?{urlencode(params)}"


def exchange_code_for_tokens(code: str) -> dict:
    try:
        response = requests.post(
            JIRA_OAUTH_TOKEN_URL,
            json={
                "grant_type": "authorization_code",
                "client_id": JIRA_OAUTH_CLIENT_ID,
                "client_secret": JIRA_OAUTH_CLIENT_SECRET,
                "code": code,
                "redirect_uri": JIRA_OAUTH_REDIRECT_URI
            },
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(f"Token exchange failed: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange authorization code for tokens: {e.response.text}"
        )
    except Exception as e:
        logger.error(f"Token exchange error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange authorization code for tokens: {str(e)}"
        )


def refresh_access_token(refresh_token: str) -> dict:
    try:
        response = requests.post(
            JIRA_OAUTH_TOKEN_URL,
            json={
                "grant_type": "refresh_token",
                "client_id": JIRA_OAUTH_CLIENT_ID,
                "client_secret": JIRA_OAUTH_CLIENT_SECRET,
                "refresh_token": refresh_token
            },
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=401,
            detail=f"Failed to refresh access token: {str(e)}"
        )


def get_accessible_resources(access_token: str) -> list:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(
            f"{JIRA_API_BASE_URL}/oauth/token/accessible-resources",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch accessible resources: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=401,
            detail=f"Failed to fetch accessible resources: {str(e)}"
        )


def get_cloud_id(access_token: str) -> str:
    resources = get_accessible_resources(access_token)
    if not resources:
        raise HTTPException(
            status_code=401,
            detail="No accessible Jira sites found for this account"
        )
    
    for resource in resources:
        if JIRA_DOMAIN and JIRA_DOMAIN in resource.get("url", ""):
            return resource["id"]
    
    return resources[0]["id"]


def get_user_info(access_token: str) -> dict:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        cloud_id = get_cloud_id(access_token)
        user_url = f"{JIRA_API_BASE_URL}/ex/jira/{cloud_id}/rest/api/3/myself"
        
        response = requests.get(user_url, headers=headers)
        response.raise_for_status()
        
        user_data = response.json()
        user_data["cloudId"] = cloud_id
        return user_data
    except HTTPException:
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(f"Failed to fetch user info: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=401,
            detail=f"Failed to fetch user info: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to fetch user info: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=401,
            detail=f"Failed to fetch user info: {str(e)}"
        )
