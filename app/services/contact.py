"""
Contact Service
Handles all business logic for contact submissions
"""

from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
import logging

from ..core import get_contact_collection, InvalidObjectIDException, ContactNotFoundException, DatabaseException
from ..utils import is_valid_object_id, format_contact_response, create_list_response

logger = logging.getLogger(__name__)


class ContactService:
    """Service for managing contact submissions"""
    
    @staticmethod
    async def create_contact(contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new contact submission
        
        Args:
            contact_data: Contact form data
            
        Returns:
            Created contact document
        """
        try:
            collection = await get_contact_collection()
            
            # Add metadata
            contact_data["date"] = datetime.utcnow()
            contact_data["status"] = "new"
            contact_data["created_at"] = datetime.utcnow()
            
            result = await collection.insert_one(contact_data)
            created = await collection.find_one({"_id": result.inserted_id})
            
            return format_contact_response(created)
            
        except Exception as e:
            logger.error(f"Error creating contact: {str(e)}")
            raise DatabaseException(f"Failed to create contact: {str(e)}")
    
    @staticmethod
    async def get_all_contacts(skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """
        Get all contact submissions (admin endpoint)
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            Dictionary with paginated contacts
        """
        try:
            collection = await get_contact_collection()
            
            total = await collection.count_documents({})
            
            cursor = collection.find({}).skip(skip).limit(limit).sort("date", -1)
            items = []
            async for document in cursor:
                items.append(format_contact_response(document))
            
            return create_list_response(items, total, skip, limit)
            
        except Exception as e:
            logger.error(f"Error fetching contacts: {str(e)}")
            raise DatabaseException(f"Failed to fetch contacts: {str(e)}")
    
    @staticmethod
    async def get_contact_by_id(id: str) -> Dict[str, Any]:
        """
        Get specific contact submission by ID
        
        Args:
            id: Contact ID
            
        Returns:
            Contact document
            
        Raises:
            InvalidObjectIDException: If ID format is invalid
            ContactNotFoundException: If contact not found
        """
        try:
            if not is_valid_object_id(id):
                raise InvalidObjectIDException(f"Invalid contact ID format: {id}")
            
            collection = await get_contact_collection()
            document = await collection.find_one({"_id": ObjectId(id)})
            
            if not document:
                raise ContactNotFoundException(f"Contact not found with ID: {id}")
            
            return format_contact_response(document)
            
        except (InvalidObjectIDException, ContactNotFoundException):
            raise
        except Exception as e:
            logger.error(f"Error fetching contact {id}: {str(e)}")
            raise DatabaseException(f"Failed to fetch contact: {str(e)}")
    
    @staticmethod
    async def get_contact_count(status: Optional[str] = None) -> int:
        """
        Get total number of contact submissions
        
        Args:
            status: Optional status filter
            
        Returns:
            Count of contacts
        """
        try:
            collection = await get_contact_collection()
            
            query = {}
            if status:
                query["status"] = status
            
            return await collection.count_documents(query)
            
        except Exception as e:
            logger.error(f"Error counting contacts: {str(e)}")
            raise DatabaseException(f"Failed to count contacts: {str(e)}")
    
    @staticmethod
    async def update_contact_status(id: str, status: str) -> Dict[str, Any]:
        """
        Update contact submission status (admin function)
        
        Args:
            id: Contact ID
            status: New status
            
        Returns:
            Updated contact document
            
        Raises:
            InvalidObjectIDException: If ID format is invalid
            ContactNotFoundException: If contact not found
        """
        try:
            if not is_valid_object_id(id):
                raise InvalidObjectIDException(f"Invalid contact ID format: {id}")
            
            collection = await get_contact_collection()
            
            # Check if exists
            existing = await collection.find_one({"_id": ObjectId(id)})
            if not existing:
                raise ContactNotFoundException(f"Contact not found with ID: {id}")
            
            # Update status
            await collection.update_one(
                {"_id": ObjectId(id)},
                {
                    "$set": {
                        "status": status,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Return updated document
            updated = await collection.find_one({"_id": ObjectId(id)})
            return format_contact_response(updated)
            
        except (InvalidObjectIDException, ContactNotFoundException):
            raise
        except Exception as e:
            logger.error(f"Error updating contact {id}: {str(e)}")
            raise DatabaseException(f"Failed to update contact: {str(e)}")
    
    @staticmethod
    async def get_contact_stats() -> Dict[str, Any]:
        """
        Get contact statistics
        
        Returns:
            Dictionary with contact statistics
        """
        try:
            collection = await get_contact_collection()
            
            total = await collection.count_documents({})
            new = await collection.count_documents({"status": "new"})
            reviewed = await collection.count_documents({"status": "reviewed"})
            replied = await collection.count_documents({"status": "replied"})
            archived = await collection.count_documents({"status": "archived"})
            
            return {
                "total": total,
                "new": new,
                "reviewed": reviewed,
                "replied": replied,
                "archived": archived
            }
            
        except Exception as e:
            logger.error(f"Error getting contact stats: {str(e)}")
            raise DatabaseException(f"Failed to get contact stats: {str(e)}")
