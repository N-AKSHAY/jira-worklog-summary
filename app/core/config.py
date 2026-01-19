from dotenv import load_dotenv
import os

load_dotenv()

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "app/ui/templates")

JIRA_OAUTH_CLIENT_ID = os.getenv("JIRA_OAUTH_CLIENT_ID")
JIRA_OAUTH_CLIENT_SECRET = os.getenv("JIRA_OAUTH_CLIENT_SECRET")
JIRA_OAUTH_REDIRECT_URI = os.getenv("JIRA_OAUTH_REDIRECT_URI", "http://localhost:8000/auth/callback")
JIRA_OAUTH_AUTHORIZE_URL = os.getenv(
    "JIRA_OAUTH_AUTHORIZE_URL",
    f"https://{JIRA_DOMAIN}/plugins/servlet/oauth/authorize" if JIRA_DOMAIN else None
)
JIRA_OAUTH_TOKEN_URL = os.getenv(
    "JIRA_OAUTH_TOKEN_URL",
    f"https://{JIRA_DOMAIN}/plugins/servlet/oauth/access-token" if JIRA_DOMAIN else None
)

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")

if not JIRA_DOMAIN:
    raise RuntimeError("Missing JIRA_DOMAIN in .env file")

if not all([JIRA_OAUTH_CLIENT_ID, JIRA_OAUTH_CLIENT_SECRET]):
    if not all([JIRA_EMAIL, JIRA_API_TOKEN]):
        raise RuntimeError("Missing Jira configuration: Either OAuth credentials or API token must be provided in .env file")
