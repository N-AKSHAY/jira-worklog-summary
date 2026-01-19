"""Jira API client implementation."""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.auth import HTTPBasicAuth
from typing import List, Dict, Any, Optional

from app.domain.interfaces import IJiraClient
from app.core.logging import get_logger
from app.core.exceptions import ExternalServiceError, AuthenticationError
from app.core.config import (
    JIRA_DOMAIN,
    JIRA_API_BASE_URL
)

logger = get_logger(__name__)


class JiraClient(IJiraClient):
    """Jira API client implementation with connection pooling."""

    def __init__(self, access_token: Optional[str] = None, cloud_id: Optional[str] = None):
        self.access_token = access_token
        self.cloud_id = cloud_id
        self._base_url = self._get_base_url()
        self._headers = {"Accept": "application/json"}
        self._auth = self._get_auth()
        self._session = self._create_session()
    
    def update_token(self, access_token: str):
        """Update the access token and refresh headers."""
        self.access_token = access_token
        self._headers["Authorization"] = f"Bearer {access_token}"
    
    def _create_session(self) -> requests.Session:
        """Create HTTP session with connection pooling and retry strategy."""
        session = requests.Session()
        session.headers.update(self._headers)
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def __del__(self):
        """Cleanup session on object destruction."""
        if hasattr(self, '_session'):
            self._session.close()

    def _get_base_url(self) -> str:
        if self.access_token and self.cloud_id:
            return f"{JIRA_API_BASE_URL}/ex/jira/{self.cloud_id}"
        return f"https://{JIRA_DOMAIN}"

    def _get_auth(self) -> Optional[HTTPBasicAuth]:
        if self.access_token:
            self._headers["Authorization"] = f"Bearer {self.access_token}"
            return None
        raise AuthenticationError("No authentication method available. Access token is required.")

    def search_issues(self, jql: str, fields: List[str], start_at: int = 0, max_results: int = 100) -> Dict[str, Any]:
        url = f"{self._base_url}/rest/api/3/search/jql"
        params = {
            "jql": jql,
            "fields": ",".join(fields),
            "startAt": start_at,
            "maxResults": max_results
        }
        response = None
        try:
            response = self._session.get(url, auth=self._auth, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.HTTPError as e:
            logger.error(
                "Jira API error",
                extra={
                    "status_code": e.response.status_code,
                    "url": url,
                    "jql": jql
                },
                exc_info=e
            )
            raise ExternalServiceError(
                message=f"Jira API error: {e.response.text}",
                service_name="Jira",
                status_code=e.response.status_code,
                details={"url": url, "jql": jql}
            )
        except Exception as e:
            logger.error(
                "Unexpected error in Jira API call",
                extra={"url": url, "jql": jql},
                exc_info=e
            )
            raise ExternalServiceError(
                message=f"Failed to query Jira API: {str(e)}",
                service_name="Jira",
                details={"url": url}
            )
        finally:
            if response:
                response.close()

    def get_issue_worklogs(self, issue_key: str) -> List[Dict[str, Any]]:
        url = f"{self._base_url}/rest/api/3/issue/{issue_key}/worklog"
        response = None
        try:
            response = self._session.get(url, auth=self._auth, timeout=30)
            response.raise_for_status()
            data = response.json().get("worklogs", [])
            return data
        except requests.exceptions.HTTPError as e:
            logger.error(
                "Failed to get worklogs",
                extra={
                    "issue_key": issue_key,
                    "status_code": e.response.status_code,
                    "url": url
                },
                exc_info=e
            )
            raise ExternalServiceError(
                message=f"Failed to retrieve worklogs for issue {issue_key}: {e.response.text}",
                service_name="Jira",
                status_code=e.response.status_code,
                details={"issue_key": issue_key, "url": url}
            )
        except Exception as e:
            logger.error(
                "Unexpected error getting worklogs",
                extra={"issue_key": issue_key, "url": url},
                exc_info=e
            )
            raise ExternalServiceError(
                message=f"Failed to retrieve worklogs: {str(e)}",
                service_name="Jira",
                details={"issue_key": issue_key}
            )
        finally:
            if response:
                response.close()

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        from app.core.auth import get_cloud_id, get_user_info as fetch_user_info
        return fetch_user_info(access_token)
