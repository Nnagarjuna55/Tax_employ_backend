"""
File upload API routes
Uses AWS S3 for cloud-based image storage
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from fastapi.responses import JSONResponse
import os
import logging
from typing import List

from ..api import auth
from ..core.s3_config import upload_image_to_s3, is_s3_configured, delete_image_from_s3

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(auth.get_current_user)
):
    """
    Upload an image file to AWS S3
    Returns the CDN URL to access the uploaded image
    """
    # Check if S3 is configured
    if not is_s3_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Image upload service is not configured. Please contact the administrator."
        )
    
    # Validate filename exists
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file: no filename provided"
        )
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    contents = await file.read()
    
    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 5MB limit"
        )
    
    # Upload to S3
    try:
        result = await upload_image_to_s3(contents, file.filename)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "url": result["url"],
                "key": result["key"],
                "filename": result["filename"],
                "size": result["size"],
            }
        )
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload image to cloud storage"
        )


@router.post("/images")
async def upload_multiple_images(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(auth.get_current_user)
):
    """
    Upload multiple image files to AWS S3
    Returns list of CDN URLs
    """
    # Check if S3 is configured
    if not is_s3_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Image upload service is not configured"
        )
    
    uploaded_files = []
    errors = []
    
    for file in files:
        try:
            # Validate filename
            if not file.filename:
                errors.append({"filename": "unknown", "error": "No filename provided"})
                continue
            
            # Validate file extension
            file_ext = os.path.splitext(file.filename)[1].lower()
            if file_ext not in ALLOWED_EXTENSIONS:
                errors.append({"filename": file.filename, "error": f"File type {file_ext} not allowed"})
                continue
            
            # Read file content
            contents = await file.read()
            
            # Validate file size
            if len(contents) > MAX_FILE_SIZE:
                errors.append({"filename": file.filename, "error": "File exceeds 5MB limit"})
                continue
            
            # Upload to S3
            result = await upload_image_to_s3(contents, file.filename)
            uploaded_files.append({
                "url": result["url"],
                "key": result["key"],
                "filename": result["filename"],
                "size": result["size"]
            })
        except Exception as e:
            logger.error(f"Error uploading {file.filename}: {str(e)}")
            errors.append({"filename": file.filename, "error": str(e)})
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "count": len(uploaded_files),
            "files": uploaded_files,
            "errors": errors if errors else None
        }
    )
