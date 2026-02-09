"""Core package initialization"""

from .config import settings
from .database import init_db, close_db, get_db, ping_db, init_indexes
from .database import get_content_collection, get_contact_collection
from .s3_config import init_s3, is_s3_configured, upload_image_to_s3, delete_image_from_s3
from .exceptions import (
    Exception,
    ValidationException,
    NotFoundException,
    ContentNotFoundException,
    ContactNotFoundException,
    InvalidObjectIDException,
    DatabaseException,
    DuplicateEntryException,
    UnauthorizedException,
    ForbiddenException,
    to_http_exception
)

__all__ = [
    "settings",
    "init_db",
    "close_db",
    "get_db",
    "ping_db",
    "init_indexes",
    "get_content_collection",
    "get_contact_collection",
    "init_s3",
    "is_s3_configured",
    "upload_image_to_s3",
    "delete_image_from_s3",
    "Exception",
    "ValidationException",
    "NotFoundException",
    "ContentNotFoundException",
    "ContactNotFoundException",
    "InvalidObjectIDException",
    "DatabaseException",
    "DuplicateEntryException",
    "UnauthorizedException",
    "ForbiddenException",
    "to_http_exception",
]
