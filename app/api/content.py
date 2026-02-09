"""
Content API Routes
Handles all HTTP endpoints for content management
"""

from fastapi import APIRouter, Query, HTTPException, status, Depends, Request
from typing import Optional
import logging

from ..schemas import ContentCreate, ContentUpdate, ContentResponse, ContentListResponse, BulkSeedResponse
from ..services import ContentService
from ..core import ContentNotFoundException, InvalidObjectIDException, DatabaseException
from ..api.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/content", tags=["Content"])


@router.api_route("/", methods=["GET", "OPTIONS"])
async def get_all_contents(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None, description="Search query")
):
    """
    Get all contents with pagination and optional search

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 10, max: 100)
    - **q**: Optional search query
    """
    # Handle OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        return {}

    try:
        return await ContentService.get_all_contents(skip, limit, q)
    except DatabaseException as e:
        logger.error(f"Error fetching contents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/item/{id}", response_model=ContentResponse)
async def get_content_by_id(id: str):
    """Get a specific content by ID"""
    try:
        return await ContentService.get_content_by_id(id)
    except InvalidObjectIDException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ContentNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.api_route("/{category}/{type}", methods=["GET", "OPTIONS"])
async def get_contents_by_filter(
    request: Request,
    category: str,
    type: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    q: Optional[str] = Query(None)
):
    """
    Get contents by category and type

    - **category**: Content category (income-tax, gst, mca, sebi, ms-office)
    - **type**: Content type (articles, news, judiciary, others)
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    - **q**: Optional search query
    """
    # Handle OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        return {}

    try:
        return await ContentService.get_contents_by_filter(category, type, skip, limit, q)
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/category/{category}", response_model=ContentListResponse)
async def get_contents_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get all contents in a specific category
    
    - **category**: Content category
    - **skip**: Number of records to skip
    - **limit**: Number of records to return
    """
    try:
        return await ContentService.get_contents_by_category(category, skip, limit)
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(
    content: ContentCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new content item (admin only)
    
    Accepts:
    - title: Article title
    - type: Content type (articles, news, judiciary, others)
    - category: Content category (income-tax, gst, mca, sebi, ms-office)
    - body: Article body (min 10 characters)
    - summary: Optional summary
    - author: Optional author name (defaults to current user)
    - images: Optional list of image URLs from AWS S3
    """
    # Check if user is admin
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create articles"
        )
    
    try:
        content_dict = content.model_dump(exclude_none=True)
        
        # Add author if not provided
        if not content_dict.get("author"):
            content_dict["author"] = current_user.get("name", current_user.get("email", "Admin"))
        
        # Ensure images is a list if provided
        if "images" in content_dict and content_dict["images"]:
            if isinstance(content_dict["images"], str):
                content_dict["images"] = [content_dict["images"]]
        
        return await ContentService.create_content(content_dict)
    except Exception as e:
        logger.error(f"Error creating content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create content: {str(e)}"
        )


@router.put("/{id}", response_model=ContentResponse)
async def update_content(id: str, content: ContentUpdate):
    """Update existing content"""
    try:
        update_dict = content.model_dump(exclude_none=True)
        return await ContentService.update_content(id, update_dict)
    except InvalidObjectIDException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ContentNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(id: str):
    """Delete content by ID"""
    try:
        deleted = await ContentService.delete_content(id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content not found"
            )
    except InvalidObjectIDException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


