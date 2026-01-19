"""Dependency injection container."""

from typing import Optional
from fastapi import Request

from app.domain.interfaces import IJiraClient, IWorklogRepository, IWorklogService
from app.infrastructure.jira_client import JiraClient
from app.domain.repositories.worklog_repository import WorklogRepository
from app.domain.services.worklog_service import WorklogService
from app.core.dependencies import AuthenticatedUser


class Container:
    """Dependency injection container."""

    @staticmethod
    def get_jira_client(
        access_token: Optional[str] = None,
        cloud_id: Optional[str] = None
    ) -> IJiraClient:
        """Create and return Jira client instance."""
        return JiraClient(access_token=access_token, cloud_id=cloud_id)

    @staticmethod
    def get_worklog_repository(jira_client: IJiraClient) -> IWorklogRepository:
        """Create and return worklog repository instance."""
        return WorklogRepository(jira_client=jira_client)

    @staticmethod
    def get_worklog_service(worklog_repository: IWorklogRepository) -> IWorklogService:
        """Create and return worklog service instance."""
        return WorklogService(worklog_repository=worklog_repository)

    @staticmethod
    def get_worklog_service_for_user(user: AuthenticatedUser) -> IWorklogService:
        """Get worklog service configured for authenticated user."""
        jira_client = Container.get_jira_client(
            access_token=user.access_token,
            cloud_id=user.cloud_id
        )
        repository = Container.get_worklog_repository(jira_client)
        service = Container.get_worklog_service(repository)
        service._user_account_id = user.account_id
        return service
