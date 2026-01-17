from dotenv import load_dotenv
import os

load_dotenv()

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_DOMAIN = os.getenv("JIRA_DOMAIN")
TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "app/ui/templates")

if not all([JIRA_EMAIL, JIRA_API_TOKEN, JIRA_DOMAIN]):
    raise RuntimeError("Missing Jira configuration in .env file")
