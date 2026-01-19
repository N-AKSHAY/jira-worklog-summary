"""Domain interfaces and abstractions."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class IJiraClient(ABC):
    """Interface for Jira API client."""

    @abstractmethod
    def search_issues(self, jql: str, fields: List[str], start_at: int = 0, max_results: int = 100) -> Dict[str, Any]:
        """Search Jira issues using JQL."""
        pass

    @abstractmethod
    def get_issue_worklogs(self, issue_key: str) -> List[Dict[str, Any]]:
        """Get worklogs for a specific issue."""
        pass

    @abstractmethod
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get current user information."""
        pass


class IWorklogRepository(ABC):
    """Interface for worklog data access."""

    @abstractmethod
    def get_worklogs_by_date_range(
        self,
        account_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Retrieve worklogs for a user within a date range."""
        pass


class IWorklogService(ABC):
    """Interface for worklog business logic."""

    @abstractmethod
    def get_worklog_summary(
        self,
        account_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """Get formatted worklog summary."""
        pass
