"""Shared exception classes."""

from typing import Optional


class BaseAppException(Exception):
    """Base exception for application errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(BaseAppException):
    """Raised when validation fails."""
    pass


class NotFoundError(BaseAppException):
    """Raised when a resource is not found."""
    pass


class AuthenticationError(BaseAppException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(BaseAppException):
    """Raised when authorization fails."""
    pass