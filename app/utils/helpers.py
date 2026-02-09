"""
Utility functions and helpers
Common functions used across the application
"""

from bson import ObjectId
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def is_valid_object_id(id_str: str) -> bool:
    """
    Validate if a string is a valid MongoDB ObjectId
    
    Args:
        id_str: String to validate
        
    Returns:
        bool: True if valid ObjectId, False otherwise
    """
    try:
        ObjectId(id_str)
        return True
    except (TypeError, ValueError):
        return False


def convert_to_object_id(id_str: str) -> Optional[ObjectId]:
    """
    Convert string to MongoDB ObjectId
    
    Args:
        id_str: String to convert
        
    Returns:
        ObjectId if valid, None otherwise
    """
    try:
        return ObjectId(id_str)
    except (TypeError, ValueError):
        return None


def format_content_response(content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format content document for API response
    Converts MongoDB ObjectId to string
    
    Args:
        content: Content document from database
        
    Returns:
        Formatted content dictionary
    """
    if not content:
        return {}
    
    formatted = dict(content)
    if "_id" in formatted:
        formatted["id"] = str(formatted.pop("_id"))
    
    return formatted


def format_contact_response(contact: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format contact document for API response
    Converts MongoDB ObjectId to string
    
    Args:
        contact: Contact document from database
        
    Returns:
        Formatted contact dictionary
    """
    if not contact:
        return {}
    
    formatted = dict(contact)
    if "_id" in formatted:
        formatted["id"] = str(formatted.pop("_id"))
    
    return formatted


def paginate_query(skip: int = 0, limit: int = 10) -> tuple:
    """
    Calculate pagination parameters
    
    Args:
        skip: Number of records to skip
        limit: Number of records to return
        
    Returns:
        tuple: (skip, limit) with validation
    """
    skip = max(0, skip)
    limit = max(1, min(limit, 100))  # Max 100 per page
    return skip, limit


def calculate_page_info(total: int, skip: int, limit: int) -> Dict[str, int]:
    """
    Calculate page information for pagination
    
    Args:
        total: Total number of records
        skip: Number of records skipped
        limit: Number of records per page
        
    Returns:
        Dictionary with page info
    """
    page = (skip // limit) + 1 if limit > 0 else 1
    total_pages = (total + limit - 1) // limit if limit > 0 else 1
    
    return {
        "page": page,
        "page_size": limit,
        "total": total,
        "total_pages": total_pages
    }


def create_list_response(items: list, total: int, skip: int, limit: int) -> Dict[str, Any]:
    """
    Create standardized list response
    
    Args:
        items: List of items
        total: Total number of items
        skip: Number of items skipped
        limit: Items per page
        
    Returns:
        Formatted list response
    """
    page_info = calculate_page_info(total, skip, limit)
    
    return {
        **page_info,
        "items": items
    }


def sanitize_input(text: str) -> str:
    """
    Sanitize user input
    Removes extra whitespace and dangerous characters
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    return text
