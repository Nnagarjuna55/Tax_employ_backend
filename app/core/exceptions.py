"""
Custom exception classes for the application
Provides typed exceptions with proper HTTP status codes
"""

from fastapi import HTTPException, status


class Exception(Exception):
    """Base exception for """
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(Exception):
    """Raised when data validation fails"""
    
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class NotFoundException(Exception):
    """Raised when a resource is not found"""
    
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class ContentNotFoundException(NotFoundException):
    """Raised when content is not found"""
    
    def __init__(self, message: str = "Content not found"):
        super().__init__(message)


class ContactNotFoundException(NotFoundException):
    """Raised when contact is not found"""
    
    def __init__(self, message: str = "Contact not found"):
        super().__init__(message)


class InvalidObjectIDException(ValidationException):
    """Raised when ObjectID format is invalid"""
    
    def __init__(self, message: str = "Invalid ID format"):
        super().__init__(message)


class DatabaseException(Exception):
    """Raised when database operation fails"""
    
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class DuplicateEntryException(ValidationException):
    """Raised when duplicate entry is attempted"""
    
    def __init__(self, message: str = "Duplicate entry"):
        super().__init__(message)


class UnauthorizedException(Exception):
    """Raised when user is unauthorized"""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class ForbiddenException(Exception):
    """Raised when user lacks permissions"""
    
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


def to_http_exception(exc: Exception) -> HTTPException:
    """Convert Exception to HTTPException"""
    return HTTPException(status_code=exc.status_code, detail=exc.message)
