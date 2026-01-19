from dotenv import load_dotenv
import os

load_dotenv()

JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")

JIRA_OAUTH_CLIENT_ID = os.getenv("JIRA_OAUTH_CLIENT_ID")
JIRA_OAUTH_CLIENT_SECRET = os.getenv("JIRA_OAUTH_CLIENT_SECRET")
JIRA_OAUTH_REDIRECT_URI = os.getenv("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")

JIRA_OAUTH_AUTHORIZE_URL = os.getenv(
    "JIRA_OAUTH_AUTHORIZE_URL",
    "https://auth.atlassian.com/authorize"
)
JIRA_OAUTH_TOKEN_URL = os.getenv(
    "JIRA_OAUTH_TOKEN_URL",
    "https://auth.atlassian.com/oauth/token"
)
JIRA_API_BASE_URL = os.getenv(
    "JIRA_API_BASE_URL",
    "https://api.atlassian.com"
)

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")

if not JIRA_DOMAIN:
    raise RuntimeError("Missing JIRA_DOMAIN in .env file")

if not all([JIRA_OAUTH_CLIENT_ID, JIRA_OAUTH_CLIENT_SECRET]):
    raise RuntimeError(
        "Missing Jira OAuth configuration: JIRA_OAUTH_CLIENT_ID and JIRA_OAUTH_CLIENT_SECRET must be provided in .env file"
    )
