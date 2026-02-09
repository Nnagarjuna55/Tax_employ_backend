"""
Content Service
Handles all business logic for content management
"""

from typing import List, Optional, Dict, Any
from bson import ObjectId
from datetime import datetime
import logging

from ..core import get_content_collection, InvalidObjectIDException, ContentNotFoundException, DatabaseException
from ..utils import is_valid_object_id, format_content_response, create_list_response

logger = logging.getLogger(__name__)


class ContentService:
    """Service for managing content operations"""
    
    @staticmethod
    async def get_all_contents(
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all contents with pagination and optional search
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            search: Optional search query
            
        Returns:
            Dictionary with paginated contents
        """
        try:
            collection = await get_content_collection()
            
            query = {}
            if search:
                query["$or"] = [
                    {"title": {"$regex": search, "$options": "i"}},
                    {"body": {"$regex": search, "$options": "i"}},
                    {"summary": {"$regex": search, "$options": "i"}},
                ]
            
            total = await collection.count_documents(query)
            
            cursor = collection.find(query).skip(skip).limit(limit).sort("date", -1)
            items = []
            async for document in cursor:
                items.append(format_content_response(document))
            
            return create_list_response(items, total, skip, limit)
            
        except Exception as e:
            logger.error(f"Error fetching all contents: {str(e)}")
            raise DatabaseException(f"Failed to fetch contents: {str(e)}")
    
    @staticmethod
    async def get_contents_by_filter(
        category: str,
        type: str,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get contents by category and type
        
        Args:
            category: Content category
            type: Content type
            skip: Number of records to skip
            limit: Number of records to return
            search: Optional search query
            
        Returns:
            Dictionary with filtered and paginated contents
        """
        try:
            collection = await get_content_collection()
            
            query = {"category": category, "type": type}
            if search:
                query["$or"] = [
                    {"title": {"$regex": search, "$options": "i"}},
                    {"body": {"$regex": search, "$options": "i"}},
                    {"summary": {"$regex": search, "$options": "i"}},
                ]
            
            total = await collection.count_documents(query)
            
            cursor = collection.find(query).skip(skip).limit(limit).sort("date", -1)
            items = []
            async for document in cursor:
                items.append(format_content_response(document))
            
            return create_list_response(items, total, skip, limit)
            
        except Exception as e:
            logger.error(f"Error fetching contents for {category}/{type}: {str(e)}")
            raise DatabaseException(f"Failed to fetch filtered contents: {str(e)}")
    
    @staticmethod
    async def get_content_by_id(id: str) -> Dict[str, Any]:
        """
        Get single content by ID
        
        Args:
            id: Content ID
            
        Returns:
            Content document
            
        Raises:
            InvalidObjectIDException: If ID format is invalid
            ContentNotFoundException: If content not found
        """
        try:
            if not is_valid_object_id(id):
                raise InvalidObjectIDException(f"Invalid content ID format: {id}")
            
            collection = await get_content_collection()
            document = await collection.find_one({"_id": ObjectId(id)})
            
            if not document:
                raise ContentNotFoundException(f"Content not found with ID: {id}")
            
            return format_content_response(document)
            
        except (InvalidObjectIDException, ContentNotFoundException):
            raise
        except Exception as e:
            logger.error(f"Error fetching content {id}: {str(e)}")
            raise DatabaseException(f"Failed to fetch content: {str(e)}")
    
    @staticmethod
    async def get_contents_by_category(
        category: str,
        skip: int = 0,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get all contents in a specific category
        
        Args:
            category: Content category
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            Dictionary with paginated contents
        """
        try:
            collection = await get_content_collection()
            
            query = {"category": category}
            total = await collection.count_documents(query)
            
            cursor = collection.find(query).skip(skip).limit(limit).sort("date", -1)
            items = []
            async for document in cursor:
                items.append(format_content_response(document))
            
            return create_list_response(items, total, skip, limit)
            
        except Exception as e:
            logger.error(f"Error fetching contents for category {category}: {str(e)}")
            raise DatabaseException(f"Failed to fetch category contents: {str(e)}")
    
    @staticmethod
    async def create_content(content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new content
        
        Args:
            content_data: Content data
            
        Returns:
            Created content document
        """
        try:
            collection = await get_content_collection()
            
            # Add metadata - use provided date or current date
            if "date" not in content_data or not content_data.get("date"):
                content_data["date"] = datetime.utcnow()
            else:
                # Convert string date to datetime if needed
                if isinstance(content_data["date"], str):
                    try:
                        content_data["date"] = datetime.fromisoformat(content_data["date"].replace('Z', '+00:00'))
                    except:
                        content_data["date"] = datetime.utcnow()
            content_data["created_at"] = datetime.utcnow()
            
            result = await collection.insert_one(content_data)
            created = await collection.find_one({"_id": result.inserted_id})
            
            return format_content_response(created)
            
        except Exception as e:
            logger.error(f"Error creating content: {str(e)}")
            raise DatabaseException(f"Failed to create content: {str(e)}")
    
    @staticmethod
    async def update_content(id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update existing content
        
        Args:
            id: Content ID
            update_data: Fields to update
            
        Returns:
            Updated content document
            
        Raises:
            InvalidObjectIDException: If ID format is invalid
            ContentNotFoundException: If content not found
        """
        try:
            if not is_valid_object_id(id):
                raise InvalidObjectIDException(f"Invalid content ID format: {id}")
            
            collection = await get_content_collection()
            
            # Check if content exists
            existing = await collection.find_one({"_id": ObjectId(id)})
            if not existing:
                raise ContentNotFoundException(f"Content not found with ID: {id}")
            
            # Remove None values
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            if update_data:
                update_data["updated_at"] = datetime.utcnow()
                await collection.update_one(
                    {"_id": ObjectId(id)},
                    {"$set": update_data}
                )
            
            # Return updated document
            updated = await collection.find_one({"_id": ObjectId(id)})
            return format_content_response(updated)
            
        except (InvalidObjectIDException, ContentNotFoundException):
            raise
        except Exception as e:
            logger.error(f"Error updating content {id}: {str(e)}")
            raise DatabaseException(f"Failed to update content: {str(e)}")
    
    @staticmethod
    async def delete_content(id: str) -> bool:
        """
        Delete content by ID
        
        Args:
            id: Content ID
            
        Returns:
            True if deleted, False otherwise
            
        Raises:
            InvalidObjectIDException: If ID format is invalid
        """
        try:
            if not is_valid_object_id(id):
                raise InvalidObjectIDException(f"Invalid content ID format: {id}")
            
            collection = await get_content_collection()
            result = await collection.delete_one({"_id": ObjectId(id)})
            
            return result.deleted_count > 0
            
        except InvalidObjectIDException:
            raise
        except Exception as e:
            logger.error(f"Error deleting content {id}: {str(e)}")
            raise DatabaseException(f"Failed to delete content: {str(e)}")
    
    @staticmethod
    async def get_content_count(
        category: Optional[str] = None,
        type: Optional[str] = None
    ) -> int:
        """
        Get count of contents with optional filters
        
        Args:
            category: Filter by category (optional)
            type: Filter by type (optional)
            
        Returns:
            Count of matching contents
        """
        try:
            collection = await get_content_collection()
            
            query = {}
            if category:
                query["category"] = category
            if type:
                query["type"] = type
            
            return await collection.count_documents(query)
            
        except Exception as e:
            logger.error(f"Error counting contents: {str(e)}")
            raise DatabaseException(f"Failed to count contents: {str(e)}")
    
