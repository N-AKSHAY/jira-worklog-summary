import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urlencode

from app.core.config import (
    JIRA_OAUTH_CLIENT_ID,
    JIRA_OAUTH_CLIENT_SECRET,
    JIRA_OAUTH_REDIRECT_URI,
    JIRA_OAUTH_AUTHORIZE_URL,
    JIRA_OAUTH_TOKEN_URL,
    JIRA_API_BASE_URL,
    JIRA_DOMAIN
)
from app.core.logging import get_logger
from app.core.exceptions import AuthenticationError, ExternalServiceError

logger = get_logger(__name__)
OAUTH_SCOPES = "read:jira-work read:jira-user offline_access"

_oauth_session = None


def _get_oauth_session() -> requests.Session:
    """Get or create shared OAuth session with connection pooling."""
    global _oauth_session
    if _oauth_session is None:
        _oauth_session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"]
        )
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=5,
            pool_maxsize=10
        )
        _oauth_session.mount("http://", adapter)
        _oauth_session.mount("https://", adapter)
    return _oauth_session


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
    session = _get_oauth_session()
    response = None
    try:
        response = session.post(
            JIRA_OAUTH_TOKEN_URL,
            json={
                "grant_type": "authorization_code",
                "client_id": JIRA_OAUTH_CLIENT_ID,
                "client_secret": JIRA_OAUTH_CLIENT_SECRET,
                "code": code,
                "redirect_uri": JIRA_OAUTH_REDIRECT_URI
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logger.error(
            "Token exchange failed",
            extra={"status_code": e.response.status_code},
            exc_info=e
        )
        raise ExternalServiceError(
            message=f"Failed to exchange authorization code for tokens: {e.response.text}",
            service_name="Jira OAuth",
            status_code=e.response.status_code
        )
    except Exception as e:
        logger.error("Token exchange error", exc_info=e)
        raise ExternalServiceError(
            message=f"Failed to exchange authorization code for tokens: {str(e)}",
            service_name="Jira OAuth"
        )
    finally:
        if response:
            response.close()


def refresh_access_token(refresh_token: str) -> dict:
    session = _get_oauth_session()
    response = None
    try:
        response = session.post(
            JIRA_OAUTH_TOKEN_URL,
            json={
                "grant_type": "refresh_token",
                "client_id": JIRA_OAUTH_CLIENT_ID,
                "client_secret": JIRA_OAUTH_CLIENT_SECRET,
                "refresh_token": refresh_token
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error("Token refresh error", exc_info=e)
        raise AuthenticationError(f"Failed to refresh access token: {str(e)}")
    finally:
        if response:
            response.close()


def get_accessible_resources(access_token: str) -> list:
    session = _get_oauth_session()
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = None
    try:
        response = session.get(
            f"{JIRA_API_BASE_URL}/oauth/token/accessible-resources",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error("Failed to fetch accessible resources", exc_info=e)
        raise ExternalServiceError(
            message=f"Failed to fetch accessible resources: {str(e)}",
            service_name="Jira API"
        )
    finally:
        if response:
            response.close()


def get_cloud_id(access_token: str) -> str:
    resources = get_accessible_resources(access_token)
    if not resources:
        raise AuthenticationError("No accessible Jira sites found for this account")
    
    for resource in resources:
        if JIRA_DOMAIN and JIRA_DOMAIN in resource.get("url", ""):
            return resource["id"]
    
    return resources[0]["id"]


def get_user_info(access_token: str) -> dict:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    response = None
    try:
        cloud_id = get_cloud_id(access_token)
        user_url = f"{JIRA_API_BASE_URL}/ex/jira/{cloud_id}/rest/api/3/myself"
        
        session = _get_oauth_session()
        response = session.get(user_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        user_data = response.json()
        user_data["cloudId"] = cloud_id
        return user_data
    except (AuthenticationError, ExternalServiceError):
        raise
    except requests.exceptions.HTTPError as e:
        logger.error(
            "Failed to fetch user info",
            extra={"status_code": e.response.status_code},
            exc_info=e
        )
        raise ExternalServiceError(
            message=f"Failed to fetch user info: {str(e)}",
            service_name="Jira API",
            status_code=e.response.status_code
        )
    except Exception as e:
        logger.error("Failed to fetch user info", exc_info=e)
        raise ExternalServiceError(
            message=f"Failed to fetch user info: {str(e)}",
            service_name="Jira API"
        )
    finally:
        if response:
            response.close()
