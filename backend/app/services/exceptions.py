"""Typed exceptions for the service layer."""
from typing import Optional


class ServiceException(Exception):
    """Base service exception."""
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(message)


class ValidationException(ServiceException):
    """Request validation failed."""
    pass


class WorkflowException(ServiceException):
    """Workflow operation failed."""
    pass


class AuthorizationException(ServiceException):
    """Authorization failed."""
    pass


class ToolException(ServiceException):
    """Tool operation failed."""
    pass


class ConfigurationException(ServiceException):
    """Configuration error."""
    pass