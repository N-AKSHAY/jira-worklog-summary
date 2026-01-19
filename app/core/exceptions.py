"""Custom exception classes for the application."""

from typing import Optional, Dict, Any


class BaseApplicationException(Exception):
    """Base exception for all application exceptions."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseApplicationException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details
        )


class AuthenticationError(BaseApplicationException):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication required", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(BaseApplicationException):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Not authorized", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class NotFoundError(BaseApplicationException):
    """Exception for resource not found errors."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details
        )


class ExternalServiceError(BaseApplicationException):
    """Exception for external service errors."""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        status_code: int = 502,
        details: Optional[Dict[str, Any]] = None
    ):
        merged_details = details.copy() if details else {}
        merged_details["service"] = service_name
        super().__init__(
            message=message,
            status_code=status_code,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=merged_details
        )


class RepositoryError(BaseApplicationException):
    """Exception for repository/data access errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="REPOSITORY_ERROR",
            details=details
        )


class ServiceError(BaseApplicationException):
    """Exception for service/business logic errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="SERVICE_ERROR",
            details=details
        )
