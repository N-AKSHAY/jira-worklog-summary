"""Base classes for repository and service patterns."""

from abc import ABC
from typing import Any, Dict, Optional
from app.core.logging import get_logger
from app.core.exceptions import (
    RepositoryError,
    ServiceError,
    ExternalServiceError,
    AuthenticationError
)


class BaseRepository(ABC):
    """Base repository class with common functionality."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def _handle_error(
        self,
        error: Exception,
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Handle repository errors consistently."""
        self.logger.error(
            f"Repository error in {operation}",
            extra={
                "operation": operation,
                "repository": self.__class__.__name__,
                **(context or {})
            },
            exc_info=error
        )
        
        if isinstance(error, (RepositoryError, ServiceError, ExternalServiceError, AuthenticationError)):
            raise error
        
        raise RepositoryError(
            message=f"Failed to {operation}: {str(error)}",
            details=context or {}
        )


class BaseService(ABC):
    """Base service class with common functionality."""
    
    def __init__(self):
        self.logger = get_logger(self.__class__.__name__)
    
    def _handle_error(
        self,
        error: Exception,
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Handle service errors consistently."""
        self.logger.error(
            f"Service error in {operation}",
            extra={
                "operation": operation,
                "service": self.__class__.__name__,
                **(context or {})
            },
            exc_info=error
        )
        
        if isinstance(error, (RepositoryError, ServiceError, ExternalServiceError, AuthenticationError)):
            raise error
        
        raise ServiceError(
            message=f"Failed to {operation}: {str(error)}",
            details=context or {}
        )
