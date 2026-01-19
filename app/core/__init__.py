"""Core application components: configuration, authentication, session management."""

from app.core.config import (
    JIRA_DOMAIN,
    JIRA_OAUTH_CLIENT_ID,
    JIRA_OAUTH_CLIENT_SECRET,
    JIRA_OAUTH_REDIRECT_URI,
    JIRA_API_BASE_URL,
    SECRET_KEY
)
from app.core.dependencies import AuthenticatedUser, get_current_user
from app.core.session import (
    get_access_token,
    get_refresh_token,
    get_user_info,
    set_access_token,
    set_refresh_token,
    set_user_info
)

__all__ = [
    "JIRA_DOMAIN",
    "JIRA_OAUTH_CLIENT_ID",
    "JIRA_OAUTH_CLIENT_SECRET",
    "JIRA_OAUTH_REDIRECT_URI",
    "JIRA_API_BASE_URL",
    "SECRET_KEY",
    "AuthenticatedUser",
    "get_current_user",
    "get_access_token",
    "get_refresh_token",
    "get_user_info",
    "set_access_token",
    "set_refresh_token",
    "set_user_info",
]
