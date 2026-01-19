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
from app.core.exceptions import (
    BaseApplicationException,
    ValidationError,
    AuthenticationError,
    ExternalServiceError,
    RepositoryError,
    ServiceError
)
from app.core.logging import get_logger
from app.core.container import Container
from app.core.base import BaseRepository, BaseService
from app.core.validators import (
    validate_date_range,
    validate_required
)
from app.core.constants import (
    API_V1_PREFIX,
    API_TAGS,
    ROUTES,
    SESSION_KEYS,
    DATE_FORMAT,
    DATE_FORMAT_DISPLAY
)

__all__ = [
    # Config
    "JIRA_DOMAIN",
    "JIRA_OAUTH_CLIENT_ID",
    "JIRA_OAUTH_CLIENT_SECRET",
    "JIRA_OAUTH_REDIRECT_URI",
    "JIRA_API_BASE_URL",
    "SECRET_KEY",
    # Dependencies
    "AuthenticatedUser",
    "get_current_user",
    # Session
    "get_access_token",
    "get_refresh_token",
    "get_user_info",
    "set_access_token",
    "set_refresh_token",
    "set_user_info",
    # Exceptions
    "BaseApplicationException",
    "ValidationError",
    "AuthenticationError",
    "ExternalServiceError",
    "RepositoryError",
    "ServiceError",
    # Utilities
    "get_logger",
    "Container",
    "BaseRepository",
    "BaseService",
    # Validators
    "validate_date_range",
    "validate_required",
    # Constants
    "API_V1_PREFIX",
    "API_TAGS",
    "ROUTES",
    "SESSION_KEYS",
    "DATE_FORMAT",
    "DATE_FORMAT_DISPLAY",
]
