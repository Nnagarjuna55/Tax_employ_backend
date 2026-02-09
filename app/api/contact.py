"""
Contact API Routes
Handles all HTTP endpoints for contact form submissions
"""

from fastapi import APIRouter, Query, HTTPException, status
import logging

from ..schemas import ContactCreate, ContactResponse, ContactListResponse, ContactCountResponse
from ..services import ContactService
from ..core import ContactNotFoundException, InvalidObjectIDException, DatabaseException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contact", tags=["Contact"])


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(contact: ContactCreate):
    """
    Submit a new contact form
    
    Returns:
        Created contact submission with ID and timestamp
    """
    try:
        contact_dict = contact.model_dump(exclude_none=True)
        return await ContactService.create_contact(contact_dict)
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/", response_model=ContactListResponse)
async def get_all_contacts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Get all contact submissions (Admin endpoint)
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 10, max: 100)
    """
    try:
        return await ContactService.get_all_contacts(skip, limit)
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{id}", response_model=ContactResponse)
async def get_contact_by_id(id: str):
    """
    Get specific contact submission by ID
    
    - **id**: Contact submission ID
    """
    try:
        return await ContactService.get_contact_by_id(id)
    except InvalidObjectIDException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ContactNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/count", response_model=ContactCountResponse)
async def get_contact_count():
    """
    Get contact submission statistics
    
    Returns:
        Total count and breakdown by status
    """
    try:
        stats = await ContactService.get_contact_stats()
        return ContactCountResponse(
            count=stats["total"],
            new_count=stats["new"],
            reviewed_count=stats["reviewed"],
            replied_count=stats["replied"],
            archived_count=stats["archived"]
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
