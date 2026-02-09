"""
AWS S3 configuration for image storage
Handles cloud-based image storage and CDN delivery via AWS S3
"""

import boto3
import os
import logging
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# AWS S3 configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME", "")
AWS_S3_REGION = os.getenv("AWS_S3_REGION", "us-east-1")
AWS_S3_CUSTOM_DOMAIN = os.getenv("AWS_S3_CUSTOM_DOMAIN", "")  # Optional CloudFront or custom domain

# S3 client
s3_client = None


def init_s3():
    """Initialize S3 client"""
    global s3_client
    
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME]):
        logger.warning(
            "AWS S3 credentials not fully configured. "
            "Image uploads will be disabled."
        )
        return False
    
    try:
        s3_client = boto3.client(
            "s3",
            region_name=AWS_S3_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        
        # Test connection by listing buckets
        s3_client.list_buckets()
        logger.info("S3 client initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize S3 client: {str(e)}")
        return False


def generate_s3_key(filename: str, folder: str = "") -> str:
    """
    Generate a unique S3 key for the file
    
    Args:
        filename: Original filename
        folder: S3 folder prefix
    
    Returns:
        str: Unique S3 key path
    """
    # Get file extension
    _, ext = os.path.splitext(filename)
    
    # Generate unique filename
    unique_id = uuid.uuid4().hex[:8]
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    s3_key = f"{folder}/{timestamp}/{unique_id}{ext}"
    
    return s3_key


async def upload_image_to_s3(file_data: bytes, filename: str, folder: str = "") -> dict:
    """
    Upload image to AWS S3
    Uses asyncio executor to run blocking boto3 operations
    
    Args:
        file_data: Binary file data
        filename: Original filename
        folder: S3 folder prefix
    
    Returns:
        dict: Upload response with url and key
    
    Raises:
        Exception: If upload fails
    """
    if not is_s3_configured():
        raise Exception("S3 is not configured")
    
    # Ensure S3 client is initialized
    if s3_client is None:
        if not init_s3():
            raise Exception("S3 client initialization failed")
    
    import asyncio
    
    try:
        # Generate S3 key
        s3_key = generate_s3_key(filename, folder)
        
        # Determine content type
        content_type = "image/jpeg"
        if filename.lower().endswith(".png"):
            content_type = "image/png"
        elif filename.lower().endswith(".gif"):
            content_type = "image/gif"
        elif filename.lower().endswith(".webp"):
            content_type = "image/webp"
        
        # Run blocking boto3 operation in executor
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: s3_client.put_object(
                Bucket=AWS_S3_BUCKET_NAME,
                Key=s3_key,
                Body=file_data,
                ContentType=content_type,
                ServerSideEncryption="AES256",
                Metadata={
                    "original-filename": filename,
                    "uploaded-at": datetime.utcnow().isoformat()
                }
            )
        )
        
        # Generate URL
        if AWS_S3_CUSTOM_DOMAIN:
            # Use custom domain (CloudFront or custom domain)
            url = f"https://{AWS_S3_CUSTOM_DOMAIN}/{s3_key}"
        else:
            # Use S3 default URL
            url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_REGION}.amazonaws.com/{s3_key}"
        
        logger.info(f"Successfully uploaded {filename} to S3: {s3_key}")
        
        return {
            "url": url,
            "key": s3_key,
            "filename": filename,
            "size": len(file_data),
        }
    except Exception as e:
        logger.error(f"Error uploading image to S3: {str(e)}")
        raise


async def delete_image_from_s3(s3_key: str) -> bool:
    """
    Delete image from S3
    Uses asyncio executor to run blocking boto3 operations
    
    Args:
        s3_key: S3 object key
    
    Returns:
        bool: True if deleted, False otherwise
    """
    if not is_s3_configured():
        return False
    
    # Ensure S3 client is initialized
    if s3_client is None:
        if not init_s3():
            logger.error("S3 client initialization failed")
            return False
    
    import asyncio
    
    try:
        # Run blocking boto3 operation in executor
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: s3_client.delete_object(
                Bucket=AWS_S3_BUCKET_NAME,
                Key=s3_key
            )
        )
        logger.info(f"Successfully deleted image from S3: {s3_key}")
        return True
    except Exception as e:
        logger.error(f"Error deleting image from S3: {str(e)}")
        return False


def is_s3_configured() -> bool:
    """Check if S3 is properly configured"""
    return bool(
        AWS_ACCESS_KEY_ID 
        and AWS_SECRET_ACCESS_KEY 
        and AWS_S3_BUCKET_NAME
    )


def get_s3_client():
    """Get S3 client instance"""
    global s3_client
    if s3_client is None:
        init_s3()
    return s3_client
