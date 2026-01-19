"""Application constants."""

# API Constants
API_V1_PREFIX = "/api/v1"
API_TAGS = {
    "WORKLOGS": "Worklogs",
    "AUTH": "Auth",
    "UI": "UI"
}

# Route Paths
ROUTES = {
    "ROOT": "/",
    "UI_WORKLOGS": "/ui/worklogs",
    "AUTH_LOGIN": "/auth/login",
    "AUTH_AUTHORIZE": "/auth/authorize",
    "AUTH_CALLBACK": "/auth/callback",
    "AUTH_LOGOUT": "/auth/logout",
    "AUTH_ME": "/auth/me",
    "AUTH_DENIED": "/auth/denied",
    "API_WORKLOGS_SUMMARY": f"{API_V1_PREFIX}/jira-worklogs/summary"
}

# Session Keys
SESSION_KEYS = {
    "ACCESS_TOKEN": "access_token",
    "REFRESH_TOKEN": "refresh_token",
    "USER_INFO": "user_info",
    "OAUTH_STATE": "oauth_state"
}

# Date Formats
DATE_FORMAT = "%Y-%m-%d"
DATE_FORMAT_DISPLAY = "%d-%m-%Y"

# Time Constants
SECONDS_PER_HOUR = 3600
SECONDS_PER_MINUTE = 60

# Jira API Constants
JIRA_API_VERSION = "3"
JIRA_MAX_RESULTS = 100
