"""Jira API client implementation."""

import requests
from requests.auth import HTTPBasicAuth
from typing import List, Dict, Any, Optional
import logging
from fastapi import HTTPException

from app.domain.interfaces import IJiraClient
from app.core.config import (
    JIRA_EMAIL,
    JIRA_API_TOKEN,
    JIRA_DOMAIN,
    JIRA_API_BASE_URL
)

logger = logging.getLogger(__name__)


class JiraClient(IJiraClient):
    """Jira API client implementation."""

    def __init__(self, access_token: Optional[str] = None, cloud_id: Optional[str] = None):
        self.access_token = access_token
        self.cloud_id = cloud_id
        self._base_url = self._get_base_url()
        self._headers = {"Accept": "application/json"}
        self._auth = self._get_auth()

    def _get_base_url(self) -> str:
        if self.access_token and self.cloud_id:
            return f"{JIRA_API_BASE_URL}/ex/jira/{self.cloud_id}"
        return f"https://{JIRA_DOMAIN}"

    def _get_auth(self) -> Optional[HTTPBasicAuth]:
        if self.access_token:
            self._headers["Authorization"] = f"Bearer {self.access_token}"
            return None
        if JIRA_EMAIL and JIRA_API_TOKEN:
            return HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
        raise ValueError("No authentication method available")

    def search_issues(self, jql: str, fields: List[str], start_at: int = 0, max_results: int = 100) -> Dict[str, Any]:
        url = f"{self._base_url}/rest/api/3/search/jql"
        params = {
            "jql": jql,
            "fields": ",".join(fields),
            "startAt": start_at,
            "maxResults": max_results
        }
        try:
            response = requests.get(url, headers=self._headers, auth=self._auth, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"Jira API error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Jira API error: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Unexpected error in Jira API call: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to query Jira API: {str(e)}"
            )

    def get_issue_worklogs(self, issue_key: str) -> List[Dict[str, Any]]:
        url = f"{self._base_url}/rest/api/3/issue/{issue_key}/worklog"
        try:
            response = requests.get(url, headers=self._headers, auth=self._auth)
            response.raise_for_status()
            return response.json().get("worklogs", [])
        except requests.exceptions.HTTPError as e:
            logger.error(f"Failed to get worklogs for {issue_key}: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Failed to retrieve worklogs for issue {issue_key}: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"Unexpected error getting worklogs: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve worklogs: {str(e)}"
            )

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        from app.core.auth import get_cloud_id, get_user_info as fetch_user_info
        return fetch_user_info(access_token)
